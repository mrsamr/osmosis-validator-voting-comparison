WITH

validators AS (
    SELECT address AS validator_address
         , account_address
         , label AS name
    FROM osmosis.core.fact_validators
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
