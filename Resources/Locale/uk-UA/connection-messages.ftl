whitelist-not-whitelisted = Вас немає в вайтлісті.
# proper handling for having a min/max or not
whitelist-playercount-invalid =
    { $min ->
        [0] Вайтліст для цього сервера застосовується лише нижче { $max } гравців.
       *[other]
            Вайтліст для цього сервера застосовується лише вище { $min } { $max ->
                [2147483647] -> гравців, тож ви, напевно, зможете приєднатися пізніше.
               *[other] -> гравців, та нижче { $max } гравців, тож ви, напевно, зможете приєднатися пізніше.
            }
    }
whitelist-not-whitelisted-rp = Вас немає в вайтлісті. Щоб потрапити в вайтліст, відвідайте Discord нашого проекту.
cmd-whitelistadd-desc = Додати гравця в вайтліст серверу.
cmd-whitelistadd-help = Використання: whitelistadd <username>
cmd-whitelistadd-existing = { $username } вже знаходиться в вайтлісті!
cmd-whitelistadd-added = { $username } доданий в вайтліст
cmd-whitelistadd-not-found = Не вдалося знайти гравця '{ $username }'
cmd-whitelistadd-arg-player = [player]
cmd-whitelistremove-desc = Видалити гравця з вайтлісту серверу.
cmd-whitelistremove-help = Використання: whitelistremove <username>
cmd-whitelistremove-existing = { $username } не знаходиться в вайтлісті!
cmd-whitelistremove-removed = { $username } вилучено з вайтлісту.
cmd-whitelistremove-not-found = Не вдалося знайти гравця '{ $username }'
cmd-whitelistremove-arg-player = [player]
cmd-kicknonwhitelisted-desc = Кікнути всіх гравців не в вайтлісті з серверу.
cmd-kicknonwhitelisted-help = Використання: kicknonwhitelisted
ban-banned-permanent = Цей бан можна тільки оскаржити.
ban-banned-permanent-appeal = Цей бан можна тільки оскаржити. Для цього відвідайте { $link }
ban-expires = Ви отримали бан на { $duration } хвилин, він закінчиться { $time } по UTC.
ban-banned-1 = Вам, або іншому користувачу цього комп'ютера або мережі заборонено тут грати.
ban-banned-2 = Причина бану: "{ $reason }"
ban-banned-3 = Спроби обійти цей бан, наприклад, шляхом створення нового аккаунту, будуть відслідковуватися.
soft-player-cap-full = Сервер заповнений!
panic-bunker-account-denied = Цей сервер знаходиться в режимі бункера, який часто вмикається як запобіжний захід проти рейдів. Нові підключення від акаунтів, що не відповідають певним вимогам, тимчасово не приймаються. Спробуйте пізніше
panic-bunker-account-denied-reason =Цей сервер знаходиться в режимі бункера, який часто вмикається як запобіжний захід проти рейдів. Нові підключення від акаунтів, що не відповідають певним вимогам, тимчасово не приймаються. Спробуйте пізніше. Причина: "{ $reason }"
panic-bunker-account-reason-account = Ваш акаунт на Space Station 14 занадто новий. Він має бути старшим, ніж { "$minutes" } хвилин
panic-bunker-account-reason-overall = Ваш загальний ігровий час на сервері має бути більшим за { $hours } { $hours ->
        [one] годину
        [few] години
       *[other] годин
    }.
