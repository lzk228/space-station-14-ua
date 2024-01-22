agent-id-no-new = { CAPITALIZE($card) } не дала нових доступів.
agent-id-new-1 = { CAPITALIZE($card) } дала один новий доступ.
agent-id-new =
    { CAPITALIZE($card) } дала { $number } { $number ->
        [one] новий доступ
        [few] нових доступа
       *[other] нових доступів
    }.
agent-id-card-current-name = Name:
agent-id-card-current-job = Job:
agent-id-card-job-icon-label = Job icon:
agent-id-menu-title = Agent ID Card
