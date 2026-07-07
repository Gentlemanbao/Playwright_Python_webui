SELECT
    user_uid,
    name,
    email
FROM
    t_mgmt_user
WHERE
    user_uid = %(user_uid)s