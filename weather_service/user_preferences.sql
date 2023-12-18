USE user_preferences

CREATE TABLE IF NOT EXISTS  `user_preferences` (
                                                   `id` int(11) NOT NULL,
    `user_id` varchar(255) NOT NULL,
    `city` varchar(255) NOT NULL,
    `temp_max` varchar(255) NOT NULL,
    `temp_min` varchar(255) NOT NULL,
    `rain_amount` varchar(255) NOT NULL,
    `snow_presence` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `user_preferences`
    ADD PRIMARY KEY (`id`);
ALTER TABLE `user_preferences`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;
