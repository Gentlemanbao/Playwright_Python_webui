select instruction_no,create_time from t_mgmt_instruction where instruction_no in (
select instruction_no from t_mgmt_instruction_receipt_acceptance_item where settlement_batch_no in (
select settlement_batch from t_mgmt_settlement where data_source IN (
select data_source from t_mgmt_settlement where logic_contract_code = %(logic_contract_code)s and settlement_batch IN (%(settlement_batch_data)s)) and logic_contract_code = %(logic_contract_code)s)) and instruction_state = 'FINISHED'