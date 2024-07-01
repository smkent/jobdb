import os

from jobdb.main.models import User
from jobdb.main.resources import UserResource


def test_user_export(admin_user: User) -> None:
    dataset = UserResource().export()
    assert os.linesep.join(
        [x.strip() for x in dataset.csv.splitlines()]
    ) == os.linesep.join(
        [
            "id,last_login,is_superuser,groups,user_permissions"
            ",username,first_name,last_name,email,is_staff"
            ",is_active,date_joined,phone,linkedin",
            "2,,1,,,vader,Darth,Vader,,0,1,1977-05-25"
            " 00:00:00,,https://linkedin.com/in/darth.vader",
            "1138,,1,,,luke,Luke,Skywalker,,0,1,1977-05-25"
            " 00:00:00,,https://linkedin.com/in/luke.skywalker",
            "2187,,1,,,solo,Han,Solo,,0,1,1977-05-25"
            " 00:00:00,,https://linkedin.com/in/han.solo",
        ]
    )
