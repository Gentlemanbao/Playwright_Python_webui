select
	*
from
	mgmt_data.t_mgmt_user a
join mgmt_data.t_mgmt_user_role b
where
	a.user_uid = %(user_uid)s
	and b.role_id = %(role_id)s
	and a.name = %(name)s