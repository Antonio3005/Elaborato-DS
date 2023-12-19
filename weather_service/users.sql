USE users

CREATE TABLE IF NOT EXISTS user (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255),
      password VARCHAR(255)
);
