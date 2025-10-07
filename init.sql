-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_management_system;

-- 1. 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('管理员','教师','学生') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 教师表
CREATE TABLE teachers (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男','女') NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(50),
    hire_date DATE,
    professional_title VARCHAR(50),
    FOREIGN KEY (id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 班级表
CREATE TABLE classes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    major VARCHAR(50),
    grade VARCHAR(10),
    college VARCHAR(100),
    head_teacher_id INT,
    FOREIGN KEY (head_teacher_id) REFERENCES teachers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 学生表
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男','女') NOT NULL,
    birth DATE,
    class_id INT,
    phone VARCHAR(20),
    email VARCHAR(50),
    address VARCHAR(100),
    enroll_date DATE,
    status ENUM('在读','毕业','休学','退学') DEFAULT '在读',
    FOREIGN KEY (id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 课程表
CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    teacher_id INT,
    credit FLOAT,
    capacity INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 课程时间表
CREATE TABLE course_schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    start_week INT NOT NULL,
    end_week INT NOT NULL,
    weekday ENUM('星期一','星期二','星期三','星期四','星期五','星期六','星期日') NOT NULL,
    class_period INT NOT NULL,
    classroom VARCHAR(50),
    remark VARCHAR(100),
    FOREIGN KEY (course_id) REFERENCES courses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 选课表
CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enroll_time DATE,
    status ENUM('已选','退选') DEFAULT '已选',
    UNIQUE KEY unique_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 成绩表
CREATE TABLE scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    score FLOAT,
    exam_time DATE,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 通知公告表
CREATE TABLE notices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    create_time DATETIME NOT NULL,
    publisher_id INT NOT NULL,
    FOREIGN KEY (publisher_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 考勤表
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('出勤','迟到','缺勤','请假') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. 奖惩表
CREATE TABLE rewards_punishments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    type ENUM('奖励','惩罚') NOT NULL,
    reason VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入用户数据
INSERT INTO users (username, password, role) VALUES
('admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '管理员'),
('teacher1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher4', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher5', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher6', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('teacher7', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '教师'),
('student1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student4', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student5', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student6', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student7', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student8', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student9', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student10', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student11', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student12', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student13', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student14', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student15', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student16', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student17', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student18', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student19', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student20', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student21', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student22', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student23', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student24', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生'),
('student25', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生');

-- 插入教师数据
INSERT INTO teachers (id, name, gender, phone, email, hire_date, professional_title) VALUES
(2, '张教授', '男', '13800138001', 'zhang@school.edu', '2020-09-01', '教授'),
(3, '李讲师', '女', '13800138002', 'li@school.edu', '2021-09-01', '讲师'),
(4, '王副教授', '男', '13800138003', 'wang@school.edu', '2019-09-01', '副教授'),
(5, '刘教授', '女', '13800138004', 'liu@school.edu', '2018-09-01', '教授'),
(6, '陈副教授', '男', '13800138005', 'chen@school.edu', '2020-09-01', '副教授'),
(7, '赵讲师', '女', '13800138006', 'zhao@school.edu', '2022-09-01', '讲师'),
(8, '孙教授', '男', '13800138007', 'sun@school.edu', '2017-09-01', '教授');

-- 插入班级数据
INSERT INTO classes (name, major, grade, college, head_teacher_id) VALUES
('计算机2023-1班', '计算机科学与技术', '2023', '信息学院', 2),
('计算机2023-2班', '计算机科学与技术', '2023', '信息学院', 3),
('软件2023-1班', '软件工程', '2023', '信息学院', 4),
('软件2023-2班', '软件工程', '2023', '信息学院', 5),
('数据2023-1班', '数据科学', '2023', '信息学院', 6),
('数据2023-2班', '数据科学', '2023', '信息学院', 7),
('人工智能2023-1班', '人工智能', '2023', '信息学院', 8);

-- 插入学生数据
INSERT INTO students (id, name, gender, birth, class_id, phone, email, address, enroll_date) VALUES
(7, '张三', '男', '2005-05-15', 1, '13900139001', 'zhangsan@student.edu', '北京市海淀区', '2023-09-01'),
(8, '李四', '女', '2005-07-20', 1, '13900139002', 'lisi@student.edu', '上海市浦东新区', '2023-09-01'),
(9, '王五', '男', '2005-03-10', 1, '13900139003', 'wangwu@student.edu', '广州市天河区', '2023-09-01'),
(10, '赵六', '女', '2005-12-25', 2, '13900139004', 'zhaoliu@student.edu', '深圳市南山区', '2023-09-01'),
(11, '孙七', '男', '2005-08-30', 2, '13900139005', 'sunqi@student.edu', '成都市武侯区', '2023-09-01'),
(12, '周八', '女', '2005-06-15', 2, '13900139006', 'zhouba@student.edu', '武汉市洪山区', '2023-09-01'),
(13, '吴九', '男', '2005-04-22', 3, '13900139007', 'wujiu@student.edu', '南京市鼓楼区', '2023-09-01'),
(14, '郑十', '女', '2005-09-18', 3, '13900139008', 'zhengshi@student.edu', '杭州市西湖区', '2023-09-01'),
(15, '刘一', '男', '2005-11-11', 3, '13900139009', 'liuyi@student.edu', '重庆市渝中区', '2023-09-01'),
(16, '陈二', '女', '2005-01-30', 4, '13900139010', 'chener@student.edu', '西安市雁塔区', '2023-09-01'),
(17, '杨三', '男', '2005-02-28', 4, '13900139011', 'yangsan@student.edu', '青岛市市南区', '2023-09-01'),
(18, '黄四', '女', '2005-10-05', 4, '13900139012', 'huangsi@student.edu', '大连市中山区', '2023-09-01'),
(19, '胡五', '男', '2005-07-07', 5, '13900139013', 'huwu@student.edu', '厦门市思明区', '2023-09-01'),
(20, '林六', '女', '2005-03-25', 5, '13900139014', 'linliu@student.edu', '苏州市姑苏区', '2023-09-01'),
(21, '朱七', '男', '2005-08-16', 5, '13900139015', 'zhuqi@student.edu', '天津市和平区', '2023-09-01'),
(22, '冯八', '女', '2005-04-14', 6, '13900139016', 'fengba@student.edu', '济南市历下区', '2023-09-01'),
(23, '程九', '男', '2005-06-22', 6, '13900139017', 'chengjiu@student.edu', '长沙市岳麓区', '2023-09-01'),
(24, '邓十', '女', '2005-09-30', 6, '13900139018', 'dengshi@student.edu', '南昌市东湖区', '2023-09-01'),
(25, '曾一', '男', '2005-11-20', 7, '13900139019', 'zengyi@student.edu', '合肥市蜀山区', '2023-09-01'),
(26, '彭二', '女', '2005-01-15', 7, '13900139020', 'penger@student.edu', '福州市鼓楼区', '2023-09-01'),
(27, '葛三', '男', '2005-05-28', 7, '13900139021', 'gesan@student.edu', '郑州市金水区', '2023-09-01'),
(28, '范四', '女', '2005-07-19', 7, '13900139022', 'fansi@student.edu', '昆明市五华区', '2023-09-01'),
(29, '潘五', '男', '2005-03-08', 7, '13900139023', 'panwu@student.edu', '贵阳市云岩区', '2023-09-01'),
(30, '田六', '女', '2005-12-01', 7, '13900139024', 'tianliu@student.edu', '海口市龙华区', '2023-09-01'),
(31, '许七', '男', '2005-10-11', 7, '13900139025', 'xuqi@student.edu', '太原市小店区', '2023-09-01');

-- 插入课程数据
INSERT INTO courses (name, teacher_id, credit, capacity) VALUES
('高等数学', 2, 4.0, 60),
('程序设计基础', 3, 3.0, 40),
('数据结构', 4, 3.5, 45),
('离散数学', 5, 3.0, 50),
('线性代数', 2, 3.0, 60),
('概率论与数理统计', 5, 3.0, 55),
('计算机网络', 3, 3.5, 45),
('操作系统', 4, 4.0, 40),
('数据库原理', 6, 3.5, 45),
('人工智能导论', 7, 3.0, 50),
('机器学习基础', 8, 4.0, 40),
('Python编程', 7, 3.0, 45),
('数据挖掘', 8, 3.5, 40),
('软件工程', 6, 4.0, 50),
('计算机组成原理', 2, 4.0, 45);

-- 插入课程时间表数据
INSERT INTO course_schedule (course_id, start_week, end_week, weekday, class_period, classroom) VALUES
(1, 1, 16, '星期一', 1, 'A101'),
(1, 1, 16, '星期三', 2, 'A101'),
(2, 1, 16, '星期二', 3, 'B203'),
(2, 1, 16, '星期四', 4, 'B203'),
(3, 1, 16, '星期三', 1, 'C305'),
(3, 1, 16, '星期五', 2, 'C305'),
(4, 1, 16, '星期二', 1, 'A102'),
(5, 1, 16, '星期四', 3, 'B201'),
(6, 1, 16, '星期五', 4, 'C202'),
(7, 1, 16, '星期一', 3, 'A103'),
(8, 1, 16, '星期三', 4, 'B202'),
(9, 1, 16, '星期五', 1, 'C203'),
(10, 1, 16, '星期二', 2, 'A104'),
(10, 1, 16, '星期四', 1, 'A104'),
(11, 1, 16, '星期一', 4, 'B204'),
(11, 1, 16, '星期三', 3, 'B204'),
(12, 1, 16, '星期二', 4, 'C304'),
(13, 1, 16, '星期四', 2, 'A105'),
(14, 1, 16, '星期五', 3, 'B205'),
(15, 1, 16, '星期一', 2, 'C205');

-- 插入选课数据
INSERT INTO enrollments (student_id, course_id, enroll_time, status) VALUES
(7, 1, '2023-09-01', '已选'),
(7, 2, '2023-09-01', '已选'),
(7, 3, '2023-09-01', '已选'),
(8, 1, '2023-09-01', '已选'),
(8, 2, '2023-09-01', '已选'),
(9, 1, '2023-09-01', '已选'),
(9, 3, '2023-09-01', '已选'),
(10, 2, '2023-09-01', '已选'),
(10, 4, '2023-09-01', '已选'),
(11, 1, '2023-09-01', '已选'),
(11, 5, '2023-09-01', '已选'),
(12, 3, '2023-09-01', '已选'),
(12, 6, '2023-09-01', '已选'),
(13, 4, '2023-09-01', '已选'),
(13, 7, '2023-09-01', '已选'),
(14, 5, '2023-09-01', '已选'),
(14, 8, '2023-09-01', '已选'),
(15, 6, '2023-09-01', '已选'),
(15, 9, '2023-09-01', '已选'),
(16, 10, '2023-09-01', '已选'),
(16, 11, '2023-09-01', '已选'),
(17, 12, '2023-09-01', '已选'),
(17, 13, '2023-09-01', '已选'),
(18, 14, '2023-09-01', '已选'),
(18, 15, '2023-09-01', '已选'),
(19, 1, '2023-09-01', '已选'),
(19, 10, '2023-09-01', '已选'),
(20, 2, '2023-09-01', '已选'),
(20, 11, '2023-09-01', '已选'),
(21, 3, '2023-09-01', '已选'),
(21, 12, '2023-09-01', '已选'),
(22, 4, '2023-09-01', '已选'),
(22, 13, '2023-09-01', '已选'),
(23, 5, '2023-09-01', '已选'),
(23, 14, '2023-09-01', '已选'),
(24, 6, '2023-09-01', '已选'),
(24, 15, '2023-09-01', '已选'),
(25, 7, '2023-09-01', '已选'),
(25, 10, '2023-09-01', '已选');

-- 插入成绩数据
INSERT INTO scores (enrollment_id, score, exam_time) VALUES
(1, 85.5, '2024-01-15'),
(2, 92.0, '2024-01-16'),
(3, 88.5, '2024-01-15'),
(4, 78.5, '2024-01-15'),
(5, 91.0, '2024-01-16'),
(6, 86.0, '2024-01-15'),
(7, 89.5, '2024-01-15'),
(8, 93.0, '2024-01-16'),
(9, 87.5, '2024-01-17'),
(10, 90.0, '2024-01-15'),
(11, 85.0, '2024-01-16'),
(12, 88.0, '2024-01-15'),
(13, 92.5, '2024-01-17'),
(14, 86.5, '2024-01-16'),
(15, 89.0, '2024-01-17'),
(16, 91.5, '2024-01-16'),
(17, 87.0, '2024-01-17'),
(18, 90.5, '2024-01-17'),
(19, 88.5, '2024-01-17'),
(20, 93.5, '2024-01-15'),
(21, 87.5, '2024-01-16'),
(22, 91.0, '2024-01-15'),
(23, 86.0, '2024-01-16'),
(24, 89.5, '2024-01-17'),
(25, 92.0, '2024-01-15'),
(26, 88.0, '2024-01-16'),
(27, 90.5, '2024-01-17'),
(28, 85.5, '2024-01-15'),
(29, 93.0, '2024-01-16'),
(30, 87.0, '2024-01-17');

-- 插入通知公告数据
INSERT INTO notices (title, content, create_time, publisher_id) VALUES
('开学通知', '新学期开始，请同学们按时返校', '2024-02-20 10:00:00', 1),
('期中考试安排', '期中考试将于下周开始，请做好准备', '2024-03-15 14:30:00', 2),
('教务系统维护通知', '系统将于本周六进行维护升级', '2024-03-20 16:00:00', 1),
('图书馆开放时间调整', '即日起图书馆开放时间调整为8:00-22:00', '2024-03-01 09:00:00', 3),
('运动会通知', '校运动会将于下月举行，请各班做好准备', '2024-03-10 11:00:00', 4),
('实验室安全培训', '所有学生必须参加下周的实验室安全培训', '2024-03-05 15:00:00', 5),
('创新创业大赛通知', '校级创新创业大赛开始报名', '2024-03-08 10:30:00', 6),
('学科竞赛信息', '全国大学生数学竞赛报名开始', '2024-03-12 14:00:00', 7),
('实习机会通知', '多家知名企业提供实习岗位', '2024-03-18 11:30:00', 8),
('奖学金评定通知', '本学期奖学金评定工作开始', '2024-03-25 09:00:00', 2);

-- 插入考勤数据
INSERT INTO attendance (student_id, course_id, date, status) VALUES
(7, 1, '2024-03-01', '出勤'),
(7, 2, '2024-03-01', '出勤'),
(8, 1, '2024-03-01', '出勤'),
(9, 1, '2024-03-01', '请假'),
(10, 2, '2024-03-01', '出勤'),
(11, 1, '2024-03-01', '出勤'),
(12, 3, '2024-03-01', '出勤'),
(13, 4, '2024-03-01', '迟到'),
(14, 5, '2024-03-01', '出勤'),
(15, 6, '2024-03-01', '出勤'),
(7, 1, '2024-03-02', '出勤'),
(8, 2, '2024-03-02', '出勤'),
(9, 3, '2024-03-02', '出勤'),
(10, 4, '2024-03-02', '出勤'),
(11, 5, '2024-03-02', '请假'),
(16, 10, '2024-03-01', '出勤'),
(17, 12, '2024-03-01', '出勤'),
(18, 14, '2024-03-01', '迟到'),
(19, 1, '2024-03-01', '出勤'),
(20, 2, '2024-03-01', '出勤'),
(21, 3, '2024-03-02', '请假'),
(22, 4, '2024-03-02', '出勤'),
(23, 5, '2024-03-02', '出勤'),
(24, 6, '2024-03-02', '出勤'),
(25, 7, '2024-03-02', '迟到');

-- 插入奖惩数据
INSERT INTO rewards_punishments (student_id, type, reason, date) VALUES
(7, '奖励', '学习成绩优异，获得奖学金', '2024-01-20'),
(8, '奖励', '积极参与社会实践', '2024-02-15'),
(9, '奖励', '担任班级干部表现优秀', '2024-01-25'),
(10, '惩罚', '旷课三次', '2024-03-10'),
(11, '奖励', '运动会表现突出', '2024-03-05'),
(12, '奖励', '志愿服务表现优秀', '2024-02-20'),
(13, '惩罚', '实验课迟到', '2024-03-15'),
(14, '奖励', '创新竞赛获奖', '2024-02-28'),
(15, '奖励', '文明宿舍评比第一', '2024-03-01'),
(16, '奖励', '程序设计大赛一等奖', '2024-02-25'),
(17, '奖励', '优秀学生干部', '2024-03-08'),
(18, '惩罚', '违反实验室规定', '2024-03-12'),
(19, '奖励', '数学建模竞赛获奖', '2024-02-18'),
(20, '奖励', '优秀团员', '2024-03-15'),
(21, '惩罚', '考试作弊', '2024-01-18');