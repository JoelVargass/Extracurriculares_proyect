CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE university_degrees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    image_path VARCHAR(255)
);

CREATE TABLE clubs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    club_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    location VARCHAR(255),
    init_hour TIME NOT NULL,
    finish_hour TIME NOT NULL,
    quota INT NOT NULL,
    teacher_name VARCHAR(255) NOT NULL,
    teacher_email VARCHAR(255) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_number VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    institutional_email VARCHAR(255) NOT NULL,
    curp VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    contact VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    club_id INT,
    degree_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (club_id) REFERENCES clubs(id),
    FOREIGN KEY (degree_id) REFERENCES university_degrees(id)
);

CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    club_id INT,
    cuatri VARCHAR(10) NOT NULL,
    group_number VARCHAR(10) NOT NULL,
    tutor_name VARCHAR(255) NOT NULL,
    seguro_social VARCHAR(20) NOT NULL,
    blood_type VARCHAR(10),
    medical_conditions VARCHAR(200),
    emergency_contact_name VARCHAR(255) NOT NULL,
    emergency_contact_phone VARCHAR(255) NOT NULL,
    contact_relationship VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);

INSERT INTO roles (title) VALUES ('admin'), ('student');
