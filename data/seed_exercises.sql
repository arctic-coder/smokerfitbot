-- Generated SQL to seed 'exercises' table (DDL + UPSERTs)
SET client_encoding = 'UTF8';

CREATE TABLE IF NOT EXISTS exercises (
  name                TEXT PRIMARY KEY,
  levels              TEXT[],
  equipment           TEXT[],
  equipment_dnf       JSONB,
  allowed_limitations TEXT[],
  muscle_group        TEXT NOT NULL,
  reps_note           TEXT,
  video_url           TEXT
);

CREATE TABLE IF NOT EXISTS seed_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

BEGIN;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подтягивания (на резинке)', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка','Турник']::text[], $json$[["Турник", "Толстая резинка"], ["Турник", "Тонкая резинка"], ["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Спина', 'максимум', 'https://drive.google.com/file/d/1nbEwFXiiGG8-CHlRwiVB3a5HD9C_Zo1l/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подтягивания (на резинке) широким хватом', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка','Турник']::text[], $json$[["Турник", "Толстая резинка"], ["Турник", "Тонкая резинка"], ["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Спина', 'максимум', 'https://drive.google.com/file/d/1fl-NyL-Mhi9iF3dtqIIRec4xitfL68m6/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подтягивания (на резинке) узким хватом', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка','Турник']::text[], $json$[["Турник", "Толстая резинка"], ["Турник", "Тонкая резинка"], ["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Спина', 'максимум', 'https://drive.google.com/file/d/1365r8n5uJoxRQBwkRTGaWBGWBJBYFWcg/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Горизонтальные подтягивания на петлях с согнутыми ногами', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Петли']::text[], $json$[["Петли"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1KQVqgMGGxB0QUB7HUufRuqsDynHmUocd/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Горизонтальные подтягивания на петлях с прямыми ногами', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Петли']::text[], $json$[["Петли"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1e7uLId3JEPS4nBiGZRNzjWfvFBHRXrIJ/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Негативные подтягивания', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Турник']::text[], $json$[["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', 'максимум', 'https://drive.google.com/file/d/1JA2sX-hdR2lr5WOm4hbvY-kTBbQX3jqp/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подтягивания в гравитроне', ARRAY['Новичок','Середнячок']::text[], ARRAY['Тренажерный зал']::text[], $json$[["Тренажерный зал"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/1XXi6hP3-99iqag895Svgz4YU1vVhGJI5/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Плавание', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/12eWgRyfpcCCC8XH3KQ4eSJhF6ylurlm8/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Плавание с гантелями', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/1pmg4pN3w1Wm5a0ePoBymkYZNVm-sHjKt/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга гантели/гири в наклоне', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Гиря','Разборные гантели']::text[], $json$[["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/1aBYPyGSX8JyaqGSlDJHhDUiIZpUVzxxU/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга двух гантелей в наклоне', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/10vtRpoemekWeVnB1nWCjwODjcZ2efIIw/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки в наклоне', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка']::text[], $json$[["Тонкая резинка"], ["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1Il5IDna5Nw1CNWgoYX2GsF84G_c37TI5/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга гантели/гири в планке', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Спина', '8-10', 'https://drive.google.com/file/d/15VM8ZJUXcp0UoE2TGfc2SxcQ_hL2Id-h/view?usp=sharing')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки стоя', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка']::text[], $json$[["Тонкая резинка"], ["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1u0-J_-Os1NOZC_o2WxcwEOVvv5in-tUc/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки сидя', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка']::text[], $json$[["Тонкая резинка"], ["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1jNinFv4PrveFkz7bWk45g9elNhLxGSTn/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки сверху', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1LUYgTkdAkIx5T3lbVHwgemRlPyul5wK_/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга верхнего блока', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тренажерный зал']::text[], $json$[["Тренажерный зал"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/1N_XMZEa9TNjj9Xd0Q3fxK2QilTyPfOzp/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга нижнего блока', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тренажерный зал']::text[], $json$[["Тренажерный зал"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/17Or7c9k7jsfFkdBXBdCHOuLwAEZz_MS4/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки к груди', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-12', 'https://drive.google.com/file/d/1copwJAXf0JvD4r1RMq_aAPTVr-bgRzK3/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Передача предмета за спиной', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '5-10', 'https://drive.google.com/file/d/1b7FSwJamd5MErnzYNBqygqzTXmU8uO_8/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тяга резинки за голову', ARRAY['Новичок','Середнячок']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Спина', '10-15', 'https://drive.google.com/file/d/1U8QJJ93d_yj1Gn1cxraryQjTUzt7JRQs/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Боковая планка', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1q-KADN5S4rPIMcpIIngkhwS-Zas5FsUo/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Планка на вытянутых руках', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1h6Djl1MO3H6Tb95DYsq9Q0qr-pUanq7m/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Планка с колен', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1UCnZ2p-9OJXIjqOZKcFVbWEGAzAgP09L/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Планка на предплечьях', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1xUJEcfAXmmQ2btZUcfLVut_37XNgwSrl/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Планка на одной руке', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Живот', 'максимум на более слабой', 'https://drive.google.com/file/d/1s8GKUDXewB5Bvza7p8ctkCct5IdL1qj6/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Планка на одной ноге', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', 'максимум на более слабой', 'https://drive.google.com/file/d/1qVoDFGzvLNPcK_q5rrTP-o9UbTiRbHA5/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы в планку', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1IggKNqXv2zUWkmMOL1wfQlcHW_x7wDJu/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Динамическая планка на петлях', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Петли']::text[], $json$[["Петли"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1yXp6bOnWhWfkw1EgCIp37Nfx2s5ypoMw/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы ног к груди в висе', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Турник']::text[], $json$[["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1NbiN8uBXakRGFc81iDAhaaoKklrPqLTE/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы ног к перекладине', ARRAY['Продолжающий']::text[], ARRAY['Турник']::text[], $json$[["Турник"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Живот', 'максимум', 'https://drive.google.com/file/d/1Kf8bQOmg5bvLO1DA7z_dS_DlSQPbHTOv/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы ног лежа', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1ytqJGslP2CSvWgSshRzb5XZC0ZKlgeFr/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы ног лежа по одной', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1SQExB5lcnc7kDnrn8SdDhHPRHbcTMJHN/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания ног лежа', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1-LRdc0V5D_xpwUByeezUyMEF77QXlR2r/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Мертвый жук', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-12', 'https://drive.google.com/file/d/1w9SYQFD_Liu3rK7W91uXvKswQY2MepNw/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Мертвый жук с гантелями', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-12', 'https://drive.google.com/file/d/1wIySSKKP39XSm_D1fk7xhkbs76gzBEjN/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания бедер с гантелью за головой', ARRAY['Новичок','Середнячок']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1j4Rrqg31WzR3kunOqWEfj7xoW19HVMTZ/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Скручивания', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-30', 'https://drive.google.com/file/d/1aSusfOoC3L18cjl3lvxv514HBy53ywpD/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Ситапы', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1hZ4pdS4cO4asLwryS5Kwwi4DXrTS3LTN/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Выходы из ситапов с замахом ногами', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Большой вес']::text[], 'Живот', '8-15', 'https://drive.google.com/file/d/1O1rpAwgiTO_p0tqQAbDp8MUx9xDQNGkI/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('V-пресс', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1J3l-DLNAO48eguW_4bf3MnOAss4xIcbt/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Гантель-колено стоя', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1eQOhpZ9Sxs2g04vAWP-wU4Zlss0I_cJt/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подведение к ситапам', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1vt5IyF7MVsoQdjN3inal2MMnB_b-UXeg/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Русские скручивания', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1gZ1r_LZ9Yt7o8KICA5MAq4OS9vlTp5v2/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Складка с гантелью', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1bto2_t6iflWuZDM0DdKU_bMGjVdiPNEi/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Складка', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Живот', '10-15', 'https://drive.google.com/file/d/1w9SYQFD_Liu3rK7W91uXvKswQY2MepNw/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-20', 'https://drive.google.com/file/d/15e3Hr24hncHhD4eGPi0PLuqEF6AFHLZ7/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания с широкой постановкой ног', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-20', 'https://drive.google.com/file/d/1MXboXlctqEQQ5dP8I2nq5WaWvXGJJJRA/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания с узкой постановкой ног', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-20', 'https://drive.google.com/file/d/1gLpPyePJp9ai9zSDZgu0rLsR8LNvw1Sh/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Выпады вперед', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/1J4PnNNdueKGeXjW0NvD5Mea6uAythckc/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Боковые выпады', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/140LTFa4k8-2VLBUdhqTe5-Wylq-bSZoU/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания с гантелью с широкой постановкой ног', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Разборные гантели']::text[], $json$[["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Большой вес']::text[], 'Ноги', '10-12', 'https://drive.google.com/file/d/1JTpDWrIra1-TFQlH4YoBjsllmsHysoHx/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания с резинкой', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка']::text[], $json$[["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1MMGVcqDUnmKZsyACThuSNIfhXKWnyP6e/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания со штангой', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Штанга']::text[], $json$[["Штанга"]]$json$::jsonb, ARRAY['Нет ограничений','Большой вес']::text[], 'Ноги', '10-12', 'https://drive.google.com/file/d/1QHBvQXr9hO9o6GawIUFVFQVLJodr3nQC/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Фронтальные приседания с гантелями/гирей', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Разборные гантели']::text[], $json$[["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Большой вес']::text[], 'Ноги', '10-12', 'https://drive.google.com/file/d/1TmfTjle-mcx2ItNsrgmKcWlxpTQFZ6DM/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Румынская тяга со штангой/гантелями/гирей', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Разборные гантели','Штанга']::text[], $json$[["Разборные гантели"], ["Гиря"], ["Штанга"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1yxbElVDyOoXuHqtNCOX2iefrOs4ltcZN/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Выпады с подъемом бедра и разгибанием колена', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1auyZ9cdwm7gPGR3Dnd5nPvc6wwBU7X3D/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Выпады с подъемом на носок', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1k-DfBXJwGRSlw9UQClc0we3GSpIq2hkq/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Выпады со сменой ног в прыжке', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', '5-10', 'https://drive.google.com/file/d/1wc4HQwBf7KoBYcmMquhKroKIeOPn8Cea/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Глубокие приседы с перекатом на колени', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1zjnjZzX-DpHaL2Xd4qrdUqZ_bxTwA6TO/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Глубокие приседы с пистолетиком', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1K3GC5QKooZ1jweTSEJnevTjI3FcKtXHI/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Креветочные приседания с касанием пола', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-10', 'https://drive.google.com/file/d/17NnmEPJAb9zi_k4nCTu0MOFokCHo9GUO/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Креветочные приседания с захватом ноги', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/1oNi0fRfb7bFiRX9UcreESCa1UvoKiiIC/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Кривая ласточка (с гантелью) на баланс', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Гиря','Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"], ["Гиря"], ["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1amY9Xzn5RxtP79sOWXO8Na9mkYXuUymD/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Наклоны на одной ноге', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1R_--EXUNgRF6PmfhT_0cj57VYFYLVWF7/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отведения-приведения с резинкой', ARRAY['Новичок','Середнячок']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '15-20', 'https://drive.google.com/file/d/10DyPgTe_nJlf3ZrgbC_pPxj4U1pdnIbU/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Пистолетики на стул', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/1OsO2sdzfWyC9dP8ZuCJncCmHYaZMwuF5/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Пистолетики на петлях', ARRAY['Середнячок']::text[], ARRAY['Петли']::text[], $json$[["Петли"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1i0W4oHY-4Xn0tN-1z--4jTElalm7JWOT/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на носки в приседе', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1Kzllqj20_ZIRVcToN6u9dITcLRJRqmeC/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы ног сидя', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1dtjc2csKvvPlVpainBgwlCClB161S0Hl/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Приседания с выпрыгиванием', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/1I35hlPEl72zXmkgwQBvU3bRosSbjYTY8/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания ноги стоя', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1pOAc-q-3IR6u_vDvZg3772gsVbKy5t5S/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Румынская тяга с резинкой', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка']::text[], $json$[["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '12-15', 'https://drive.google.com/file/d/1joV-tMFwDmYHqtrK0sUZLq2JayGH0OiO/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Ужасная планка в динамике', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', '5-15', 'https://drive.google.com/file/d/12u_O4ThnDVUMTxvZvnagZCNawibbENJ4/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Ужасная планка в статике', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Ноги', 'максимум на более слабой', 'https://drive.google.com/file/d/1sChnfvmQ0Ngxk-BuqXIYfQyz-6HPnDwP/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Фронтальные приседы с подъемом на носки', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря','Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"], ["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1YQCDZ4sgtdHrT4iCvgeRNVp4X_Ec1I0u/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Махи гирей', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Гиря']::text[], $json$[["Гиря"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Большой вес']::text[], 'Ноги', '10-15', 'https://drive.google.com/file/d/1hb_tSNS7hGontqx8PZ489bjJzHYMd1GI/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Жим платформы ногами', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тренажерный зал']::text[], $json$[["Тренажерный зал"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Ноги', '10-12', 'https://drive.google.com/file/d/1HIp0VLwp5ix1n25rQqyub5ps96xZn0hY/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Бабочка с резинкой', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Толстая резинка','Тонкая резинка']::text[], $json$[["Тонкая резинка"], ["Толстая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1F3EPNxgbmj3w_jBLfTQ9CCg5oAOFCq6o/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Жим гантелей лежа', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-12', 'https://drive.google.com/file/d/1OxWznd9QRE-mrL49sP2V2_KNXKnd0G0g/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Жим штанги лежа', ARRAY['Продолжающий']::text[], ARRAY['Штанга']::text[], $json$[["Штанга"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-12', 'https://drive.google.com/file/d/1CJmr4vu3LMsCWiqD0QgfSzaylJZT_0Er/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1A0TBc4RqHO-P-B8rTCqdxclJKoWeksQS/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Алмазные отжимания', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1gtVt4JihZjm8AxZSrJnnAQTwrbenk97r/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания с широкой постановкой рук', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1j7Ja1j8KCmIcT0ZNmxjAeNdKZ2RctmJ5/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания волной', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1N4xREvfXwVP8HUeXVjVVIRUIR_gy3rQj/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания от опоры', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1n7jQ_LmddwMsbnpeHfOOpTmM_FkEp2tN/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания с колен', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/14AqroIk48AYwwkAmS_1BpYgVZy6vISGA/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания с колен с широкой постановкой рук', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1XHblAd2DBrsqEfSBNz-uAb1PtyNKlT-J/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания с колен с узкой постановкой рук', ARRAY['Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1JYt4VA18uiLF0zs9K7DokYWHAQaqTyyz/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания на петлях', ARRAY['Середнячок','Продолжающий']::text[], ARRAY['Петли']::text[], $json$[["Петли"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/14QFc_AsI9SRN0qRFDH7hgEZHXJaS6Bm3/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания с ногами на возвышении', ARRAY['Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1celj8AFWZIM_x0xOCl8IibgGWgZpwLxF/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Сведения гантелей над грудью лежа', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1GLsAL6QwB8cEiCPOz4xAdm2M9-U-0Z2Y/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Сведения гантелей над грудью двумя способами', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10 каждого вида', 'https://drive.google.com/file/d/1XpFWgYG1cqCLPwI7pA8l8IKfIDxuxVuI/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Тренажер бабочка', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тренажерный зал']::text[], $json$[["Тренажерный зал"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1Aq2WnqWefPnP0Bzosp5_4yf3PpLLRDOB/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Обратные отжимания с прямыми ногами', ARRAY['Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/18XRZJdy8mxLHzrD1Y1tnkVAkdzNbel8H/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Обратные отжимания с согнутыми ногами', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1jmBrQkS6Z0J2wxkguEv65TEZCj4vhLuV/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания лучник от стены', ARRAY['Новичок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1K1qt_QJ51J_J81SQyPbHbIJNOEDwO9Ap/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Отжимания лучник с колен', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Грудь', 'максимум', 'https://drive.google.com/file/d/1syunPyyeLAPxU4zV1xkoLByO8q3jrYS-/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы гантелей вперед', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-12', 'https://drive.google.com/file/d/1YSGJiFNgcBpCxA9Brc8sP9nlQwu4S_sQ/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на носки с гантелями', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Икры', '10-15', 'https://drive.google.com/file/d/1Zi_S4W_v7qa_XG_UeuQf3iEFeMv7ejOm/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на носки на одной ноге', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Икры', '10-15', 'https://drive.google.com/file/d/1tOTFdmdAP8kekaUaLwr_yfrU11yiO6RP/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на носки на одной ноге с гантелями', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Разборные гантели']::text[], $json$[["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Икры', '10-30', 'https://drive.google.com/file/d/1LhQBhpc1_Dh_mTVylo2CN87VkH6Bab1r/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на носки с акцентом на внутреннюю и внешнюю стороны стопы', ARRAY['Новичок','Середнячок']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Икры', '10-15 каждого вида', 'https://drive.google.com/file/d/1eRi7oowksquWCpJBKQPNZLq_VanHV19O/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разведения гантелей в наклоне', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-12', 'https://drive.google.com/file/d/1Gv84oBBTmafyjdXYJFV6V_uB2vNoLK9R/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разведения гантелей в стороны стоя', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-12', 'https://drive.google.com/file/d/1ev83XNoqqrLx8cUcSxShBmSSRzFUm7hU/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания на трицепсы в наклоне', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Трицепсы', '10-12', 'https://drive.google.com/file/d/1IuQzEmXzTCB2u85mjoqWNTCv731LxLPs/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания на трицепсы из-за головы', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Трицепсы', '10-12', 'https://drive.google.com/file/d/1s-DfeE6GrU1a0fN-TyNKliMo9uGnK7GH/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Кубинский жим', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-12', 'https://drive.google.com/file/d/1S8PUfaGFg7q37gqi3a3fqOjJpNM8ytBm/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Трицепс + плечи с резинкой', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-15', 'https://drive.google.com/file/d/14FAtv5tmk2yfq1wxStiG4nFOdPwPNz0h/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Разгибания на трицепсы с резинкой', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Трицепсы', '10-15', 'https://drive.google.com/file/d/1lPx3ZtR1G3bjfkD0tkEMHRcncUZphYlk/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Пуловер с гантелями', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10-15', 'https://drive.google.com/file/d/1vFqFwftZ-r7gLW3RbweytqHnZsGBLq1S/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Пуловер с гантелями два вида', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Маленькие гантели','Разборные гантели']::text[], $json$[["Маленькие гантели"], ["Разборные гантели"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Грудь', '10 каждого вида', 'https://drive.google.com/file/d/1D_0HwLFZsQYRycrepgLSqTwvQadAqU0V/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы рук с резинкой в стороны', ARRAY['Новичок','Середнячок','Продолжающий']::text[], ARRAY['Тонкая резинка']::text[], $json$[["Тонкая резинка"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Плечи', '10-15', 'https://drive.google.com/file/d/108fA-nHGm2Z7h-z_dvKMQxnQ3ZprHkCY/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Подъемы на предплечье', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии']::text[], 'Плечи', '10-15', 'https://drive.google.com/file/d/1mC1g3JjX8TbwvRBO1wiRE3_RN1WgtvFY/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ('Обратные отжимания на одной руке от пола', ARRAY['Середнячок','Продолжающий']::text[], ARRAY[]::text[], $json$[["Ничего"]]$json$::jsonb, ARRAY['Нет ограничений','Больные колени','Межпозвоночные грыжи/протрузии','Большой вес']::text[], 'Трицепсы', '10-15', 'https://drive.google.com/file/d/1V9Xs1CM6dKxzeEl9kIMc-eINVMSz3WEh/view?usp=drive_link')
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
INSERT INTO seed_meta(key,value) VALUES('exercises_json_sha','6ab3bb3876c96231ec0bb1b98531c294e66707aebdd4f0cdd197e75e7d961ded') ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value, applied_at=now();
COMMIT;
