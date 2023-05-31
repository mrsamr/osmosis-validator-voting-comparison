WITH

validator_labels AS (
    SELECT address AS validator_address
         , account_address
         , label AS name
    FROM osmosis.core.fact_validators
),


validator_creation AS (
    SELECT m.attribute_value AS validator_address
         , tx.tx_from AS account_address
         , m.block_timestamp AS created_at
         , m.tx_id AS _create_tx_id
    FROM osmosis.core.fact_msg_attributes AS m
        LEFT JOIN osmosis.core.fact_transactions AS tx
            ON tx.tx_id = m.tx_id
    WHERE m.tx_succeeded = True
      AND m.msg_type = 'create_validator'
      AND m.attribute_key = 'validator'
    QUALIFY row_number() OVER (partition by validator_address order by created_at asc) = 1
),


validators AS (
    SELECT *
    FROM (
        SELECT validator_address, account_address
        FROM validator_labels
    
        UNION ALL
    
        SELECT validator_address, account_address
        FROM validator_creation
    )
    QUALIFY row_number() OVER (partition by validator_address order by validator_address) = 1
),


validator_votes AS (
    SELECT v.validator_address
         , gv.voter
         , gv.proposal_id
         , gv.vote_option
         , dvo.description AS vote
         , gv.tx_id
         , gv.block_timestamp
    
    FROM osmosis.core.fact_governance_votes AS gv
        INNER JOIN validators AS v
            ON v.account_address = gv.voter

        LEFT JOIN osmosis.core.dim_vote_options AS dvo
            ON dvo.vote_id = gv.vote_option

    WHERE gv.tx_succeeded = True
    QUALIFY row_number() OVER (partition by gv.voter, gv.proposal_id
                               order by gv.block_timestamp desc) = 1
)


SELECT validator_address
     , object_agg(proposal_id::integer, vote::variant) AS votes
     , CURRENT_TIMESTAMP AS _extracted_at
FROM validator_votes
GROUP BY validator_address
