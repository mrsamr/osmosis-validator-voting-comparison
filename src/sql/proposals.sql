WITH

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
)


SELECT proposal_id AS id
     , (CASE proposal_id WHEN 362 THEN 'Osmosis Grants Program (OGP) Renewal'
             ELSE proposal_title END) AS title
     , CURRENT_TIMESTAMP AS _extracted_at
FROM governance_proposals