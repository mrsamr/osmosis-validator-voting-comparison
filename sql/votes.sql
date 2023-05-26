WITH

validator_metadata AS (
    WITH

    missing_labels AS (
        SELECT * FROM (VALUES ('osmovaloper1tv9wnreg9z5qlxyte8526n7p3tjasndede2kj9', 'Electric'), ('osmovaloper1vcpryrtatk6c8z6tcyx9w45jsw56rvkqapgq6p', 'Twinstake'), ('osmovaloper14n8pf9uxhuyxqnqryvjdr8g68na98wn5amq3e5', 'Prism Protocol | Delegate for airdrop'), ('osmovaloper1dvpxxkksf5hrhnycsgyyjnal79lp7gp3n59t0d', 'Chill Validation'), ('osmovaloper1r7spsjagrmcfv96w5dxtttajvnxczhcpgfk74g', 'PRO Delegators'), ('osmovaloper1gw6z2kn7z7cg747czxq98yczcmauk29uzqfuw4', 'Flipside'), ('osmovaloper10w06wvmdd4xn7hr76gzrv570f7q5uweem5jcd7', 'The_Cybernetics'), ('osmovaloper1xxarc6are7zrmwvmmxkezaycepa6ttyn2gnysv', '5.0 Validator'), ('osmovaloper1ff875h5plrnyumhm3cezn85dj4hzjzjqs972w3', 'Pickaxe.it'), ('osmovaloper1v63dkhqluvkk0fsugrjp63m79556qf32r4lfgw', 'Hugo test'), ('osmovaloper1jn2tc8y4tc36pwzfd2pk009lhe420w49ryvcjf', 'Supernova'), ('osmovaloper1w6xwce25z0l5y420xnlzkxljkyxm2c4cuych7e', 'Sr20de'), ('osmovaloper1zla6q7rhrtzqyyulw86ajq9qvectddjxclc3x9', 'test-validator'), ('osmovaloper1anyeq0uugchhd7s92z44nkkku4ws52f5avm074', 'DSFDF'), ('osmovaloper1awvxsfkd9365rumd2u8j806xlmlrrjhdaxfr5q', 'testvalidator'), ('osmovaloper13qrpp886n475z2jcs552w80fwnz8zp97ajg2q9', 'fsc-osmosis-1'), ('osmovaloper1x2h5ghvxmjsy4f5qfreq9fcrr672uje0y6zsdu', 'Node X')
        ) AS labels(validator_address, validator_name)
    )

    SELECT vp.rank
         , vp.validator_address
         , fv.account_address
         , coalesce(fv.label, ml.validator_name, vp.validator_address) AS validator_name
         , vp.voting_power
    FROM (
        SELECT validator_address
             , sum(delegated_amount) AS voting_power
             , row_number() OVER (order by voting_power desc) AS rank
        FROM ( SELECT validator_address, amount / 1e6 AS delegated_amount
               FROM osmosis.core.fact_staking
               WHERE action IN ('delegate', 'redelegate')
                UNION ALL
               SELECT validator_address, -amount / 1e6 AS delegated_amount
               FROM osmosis.core.fact_staking
               WHERE action IN ('undelegate')
                UNION ALL
               SELECT redelegate_source_validator_address, -amount / 1e6 AS delegated_amount
               FROM osmosis.core.fact_staking
               WHERE action IN ('redelegate') )
        GROUP BY 1
    ) AS vp
        LEFT JOIN osmosis.core.fact_validators AS fv
            ON fv.address = vp.validator_address
        LEFT JOIN missing_labels AS ml
            ON ml.validator_address = vp.validator_address
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
    SELECT vm.validator_address
         , coalesce(vm.account_address, vc.account_address) AS account_address
         , vm.validator_name
         , coalesce(vc.created_at, '2021-06-19'::timestamp) AS created_at
    FROM validator_metadata AS vm
        LEFT JOIN validator_creation AS vc
            ON vc.validator_address = vm.validator_address
),


governance_proposals AS (
    WITH deposits AS ( SELECT proposal_id, sum(amount) AS total_deposit
                       FROM osmosis.core.fact_governance_proposal_deposits
                       GROUP BY 1 )

    SELECT p.proposal_id
         , p.proposal_title
         , d.total_deposit
         , d.total_deposit >= 500 AS meets_minimum_deposit
         , p.block_timestamp AS submitted_at
         , p.tx_id AS submit_tx
    
    FROM osmosis.core.fact_governance_submit_proposal AS p
        LEFT JOIN deposits AS d
            ON d.proposal_id = p.proposal_id

    WHERE p.tx_succeeded = True
      AND meets_minimum_deposit
      AND p.proposal_id != 371  -- excluded, duplicate proposal
      AND p.proposal_id != 338  -- excluded
      AND p.proposal_id != 312  -- excluded
      AND p.proposal_id != 311  -- excluded
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

        INNER JOIN governance_proposals AS gp
            ON gp.proposal_id = gv.proposal_id
    
    WHERE gv.tx_succeeded = True
    QUALIFY row_number() OVER (partition by gv.voter, gv.proposal_id
                               order by gv.block_timestamp desc) = 1
)


SELECT validator_address
     , object_agg(proposal_id::integer, vote::variant) AS votes
     , CURRENT_TIMESTAMP AS _extracted_at
FROM validator_votes
GROUP BY validator_address
