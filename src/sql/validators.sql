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
         , greatest(0, vp.voting_power) AS voting_power
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


deduped_names AS (
    SELECT validator_address
         , validator_name
         , voting_power
         , count(*) OVER (partition by validator_name) = 1 AS is_unique_name
         , (CASE WHEN is_unique_name THEN validator_name
                 ELSE validator_name || ' (...' || right(validator_address, 6) || ')' END) AS unique_name
    FROM validator_metadata
)


SELECT validator_address
     , unique_name AS validator_name
     , voting_power
     , CURRENT_TIMESTAMP AS _extracted_at
FROM deduped_names
ORDER BY voting_power DESC