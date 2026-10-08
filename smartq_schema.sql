
-- SmartQ schema (MySQL dialect) for Workbench reverse engineering

CREATE TABLE `auth_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB;

CREATE TABLE `services_department` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `location` varchar(120) NOT NULL,
  `description` text,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE `accounts_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(20) NOT NULL,
  `student_number` varchar(20) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_profile_dept` (`department_id`),
  CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_profile_dept` FOREIGN KEY (`department_id`) REFERENCES `services_department` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `services_service` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `description` text,
  `average_service_time_minutes` int NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_service_dept` (`department_id`),
  CONSTRAINT `fk_service_dept` FOREIGN KEY (`department_id`) REFERENCES `services_department` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `services_counter` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `department_id` bigint NOT NULL,
  `staff_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_counter_dept` (`department_id`),
  KEY `idx_counter_staff` (`staff_user_id`),
  CONSTRAINT `fk_counter_dept` FOREIGN KEY (`department_id`) REFERENCES `services_department` (`id`),
  CONSTRAINT `fk_counter_staff` FOREIGN KEY (`staff_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `queues_queueentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `queue_number` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `position` int unsigned NOT NULL,
  `counters_at_join` int unsigned DEFAULT NULL,
  `join_time` datetime(6) NOT NULL,
  `called_time` datetime(6) DEFAULT NULL,
  `arrival_time` datetime(6) DEFAULT NULL,
  `service_start_time` datetime(6) DEFAULT NULL,
  `completion_time` datetime(6) DEFAULT NULL,
  `waiting_time_minutes` int unsigned DEFAULT NULL,
  `service_duration_minutes` int unsigned DEFAULT NULL,
  `notes` text,
  `service_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  `counter_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_qe_service` (`service_id`),
  KEY `idx_qe_student` (`student_id`),
  KEY `idx_qe_counter` (`counter_id`),
  CONSTRAINT `fk_qe_service` FOREIGN KEY (`service_id`) REFERENCES `services_service` (`id`),
  CONSTRAINT `fk_qe_student` FOREIGN KEY (`student_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `fk_qe_counter` FOREIGN KEY (`counter_id`) REFERENCES `services_counter` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `accounts_notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `read` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_notif_user` (`user_id`),
  CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `accounts_auditlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int unsigned DEFAULT NULL,
  `details` text,
  `ip_address` char(39) DEFAULT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_audit_user` (`user_id`),
  CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;