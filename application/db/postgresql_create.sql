CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY,
  "user_name" varchar(50) UNIQUE NOT NULL,
  "email" varchar(50) UNIQUE NOT NULL,
  "status" varchar(50) DEFAULT 'DEACTIVATED',
  "create_date" timestamp,
  "end_date" timestamp DEFAULT NULL,
  "password_hash" varchar(255),
  "role" varchar(1024) DEFAULT 'USER',
  "group_id" int,
  "group_role" varchar(1024),
  "full_name" varchar(50),
  "workphone" varchar(50),
  "cellphone" varchar(50),
  "address" varchar(100),
  "city" varchar(50),
  "country_code" varchar(10),
  "id_number" varchar(50),
  "language" varchar(10) DEFAULT 'vi',
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "user_group" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "name" varchar(100),
  "status" varchar(50),
  "description" text,
  "create_date" timestamp,
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "configuration" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "name" varchar(100),
  "version" int,
  "status" varchar(50),
  "create_date" timestamp,
  "contents" jsonb,
  "extra" jsonb
);

CREATE TABLE "history" (
  "id" SERIAL PRIMARY KEY,
  "target_user_id" int,
  "request_user_id" int,
  "action" varchar(50),
  "status" varchar(50),
  "create_date" timestamp,
  "contents" jsonb,
  "extra" jsonb
);

CREATE TABLE "report" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "name" varchar(100),
  "status" varchar(50),
  "start_date" timestamp,
  "end_date" timestamp,
  "contents" jsonb,
  "extra" jsonb
);

CREATE TABLE "ticket" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "code" varchar(50),
  "user_id" int,
  "target_id" int,
  "status" varchar(50),
  "level" varchar(50),
  "issue" varchar(255),
  "create_date" timestamp,
  "end_date" timestamp,
  "title" varchar(255),
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "support" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "code" varchar(50),
  "user_id" int,
  "ticket_id" int,
  "status" varchar(50),
  "issue" varchar(255),
  "create_date" timestamp,
  "end_date" timestamp,
  "description" varchar(1024),
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "product" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "code" varchar(100),
  "name" varchar(100),
  "description" text,
  "create_date" timestamp,
  "end_date" timestamp,
  "info" jsonb,
  "status" varchar(50) DEFAULT 'ENABLED',
  "region_id" varchar(50),
  "pricing" jsonb,
  "extra" jsonb
);

CREATE TABLE "region" (
  "id" varchar(50) PRIMARY KEY,
  "name" varchar(50),
  "description" text,
  "create_date" timestamp,
  "status" varchar(50),
  "address" varchar(100),
  "city" varchar(50),
  "country_code" varchar(10),
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "promotion" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50) DEFAULT 'DISCOUNT',
  "name" varchar(50),
  "description" text,
  "create_date" timestamp,
  "start_date" timestamp,
  "end_date" timestamp,
  "status" varchar(50),
  "region_id" varchar(50),
  "target_product_types" jsonb,
  "target_product_ids" jsonb,
  "product_settings" jsonb,
  "user_settings" jsonb,
  "settings" jsonb,
  "discount_code" varchar(100),
  "extra" jsonb
);

CREATE TABLE "order_group" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "code" varchar(50),
  "user_id" int,
  "create_date" timestamp,
  "status" varchar(50),
  "data" jsonb,
  "notes" text,
  "extra" jsonb
);

CREATE TABLE "order" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "product_type" varchar(50),
  "code" varchar(50),
  "name" varchar(50),
  "user_id" int,
  "group_id" int,
  "price" bigint,
  "price_paid" bigint,
  "amount" int,
  "duration" varchar(50),
  "status" varchar(50),
  "create_date" timestamp,
  "start_date" timestamp,
  "end_date" timestamp,
  "discount_code" varchar(100),
  "promotion_id" int,
  "payment_type" varchar(50),
  "currency" varchar(10),
  "region_id" varchar(50),
  "data" jsonb,
  "notes" text,
  "extra" jsonb
);

CREATE TABLE "order_product" (
  "id" SERIAL PRIMARY KEY,
  "order_id" int,
  "product_id" int,
  "price" bigint,
  "price_paid" bigint,
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "billing" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "code" varchar(50),
  "user_id" int,
  "order_id" int,
  "create_date" timestamp,
  "end_date" timestamp,
  "status" varchar(50),
  "price" bigint,
  "price_paid" bigint,
  "currency" varchar(10),
  "data" jsonb,
  "notes" text,
  "extra" jsonb
);

CREATE TABLE "balance" (
  "id" SERIAL PRIMARY KEY,
  "user_id" int UNIQUE,
  "type" varchar(50),
  "create_date" timestamp,
  "end_date" timestamp,
  "status" varchar(50),
  "balance" bigint,
  "currency" varchar(10),
  "data" jsonb,
  "notes" text,
  "extra" jsonb
);

CREATE TABLE "compute" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "name" varchar(100),
  "version" int,
  "user_id" int,
  "order_id" int,
  "description" text,
  "backend_id" varchar(512),
  "backend_status" varchar(255),
  "public_ip" varchar(512),
  "create_date" timestamp,
  "end_date" timestamp,
  "status" varchar(50),
  "region_id" varchar(50),
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "session" (
  "id" SERIAL PRIMARY KEY,
  "session_id" varchar(1024) UNIQUE,
  "data" bytea,
  "expiry" timestamp
);

CREATE TABLE "lock" (
  "id" varchar(255) PRIMARY KEY,
  "timestamp" timestamp
);

CREATE TABLE "task" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar(50),
  "action" varchar(50),
  "user_id" int,
  "target_id" int,
  "target_entity" varchar(10240),
  "target_time" varchar(255),
  "target_date" varchar(255),
  "status" varchar(50),
  "create_date" timestamp,
  "start_date" timestamp,
  "end_date" timestamp,
  "description" varchar(1024),
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "public_ip" (
  "addr" varchar(255) PRIMARY KEY,
  "type" varchar(50),
  "version" int,
  "status" varchar(50),
  "mac_addr" varchar(50),
  "user_id" int,
  "compute_id" int,
  "create_date" timestamp,
  "start_date" timestamp,
  "end_date" timestamp,
  "data" jsonb,
  "extra" jsonb
);

CREATE TABLE "temp" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "version" int,
  "description" text,
  "date" timestamp,
  "data" jsonb
);

ALTER TABLE "user" ADD FOREIGN KEY ("group_id") REFERENCES "user_group" ("id");

ALTER TABLE "history" ADD FOREIGN KEY ("target_user_id") REFERENCES "user" ("id");

ALTER TABLE "history" ADD FOREIGN KEY ("request_user_id") REFERENCES "user" ("id");

ALTER TABLE "ticket" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "support" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "support" ADD FOREIGN KEY ("ticket_id") REFERENCES "ticket" ("id");

ALTER TABLE "product" ADD FOREIGN KEY ("region_id") REFERENCES "region" ("id");

ALTER TABLE "promotion" ADD FOREIGN KEY ("region_id") REFERENCES "region" ("id");

ALTER TABLE "order_group" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "order" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "order" ADD FOREIGN KEY ("group_id") REFERENCES "order_group" ("id");

ALTER TABLE "order" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotion" ("id");

ALTER TABLE "order" ADD FOREIGN KEY ("region_id") REFERENCES "region" ("id");

ALTER TABLE "order_product" ADD FOREIGN KEY ("order_id") REFERENCES "order" ("id");

ALTER TABLE "order_product" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "billing" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "billing" ADD FOREIGN KEY ("order_id") REFERENCES "order" ("id");

ALTER TABLE "balance" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "compute" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "compute" ADD FOREIGN KEY ("order_id") REFERENCES "order" ("id");

ALTER TABLE "compute" ADD FOREIGN KEY ("region_id") REFERENCES "region" ("id");

ALTER TABLE "public_ip" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "public_ip" ADD FOREIGN KEY ("compute_id") REFERENCES "compute" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

CREATE INDEX ON "user" ("user_name");

CREATE INDEX ON "user" ("email");

CREATE INDEX ON "user" ("create_date");

CREATE INDEX ON "user" ("full_name");

CREATE INDEX ON "user" ("cellphone");

CREATE INDEX ON "user" ("status");

CREATE INDEX ON "user" ("role");

CREATE INDEX ON "user" ("group_id");

CREATE INDEX ON "user" ("group_role");

CREATE INDEX ON "user" ("city");

CREATE INDEX ON "user" ("country_code");

CREATE INDEX ON "user" ("id_number");

CREATE INDEX ON "user_group" ("type");

CREATE INDEX ON "user_group" ("name");

CREATE INDEX ON "user_group" ("status");

CREATE INDEX ON "user_group" ("create_date");

CREATE INDEX ON "configuration" ("type");

CREATE INDEX ON "configuration" ("name");

CREATE INDEX ON "configuration" ("version");

CREATE UNIQUE INDEX ON "configuration" ("type", "name", "version");

CREATE INDEX ON "configuration" ("create_date");

CREATE INDEX ON "configuration" ("status");

CREATE INDEX ON "history" ("target_user_id");

CREATE INDEX ON "history" ("request_user_id");

CREATE INDEX ON "history" ("action");

CREATE INDEX ON "history" ("status");

CREATE INDEX ON "history" ("create_date");

CREATE INDEX ON "report" ("type");

CREATE INDEX ON "report" ("name");

CREATE INDEX ON "report" ("status");

CREATE INDEX ON "report" ("start_date");

CREATE INDEX ON "report" ("end_date");

CREATE INDEX ON "ticket" ("type");

CREATE INDEX ON "ticket" ("code");

CREATE INDEX ON "ticket" ("user_id");

CREATE INDEX ON "ticket" ("target_id");

CREATE INDEX ON "ticket" ("status");

CREATE INDEX ON "ticket" ("level");

CREATE INDEX ON "ticket" ("issue");

CREATE INDEX ON "ticket" ("create_date");

CREATE INDEX ON "ticket" ("end_date");

CREATE INDEX ON "support" ("type");

CREATE INDEX ON "support" ("code");

CREATE INDEX ON "support" ("user_id");

CREATE INDEX ON "support" ("ticket_id");

CREATE INDEX ON "support" ("status");

CREATE INDEX ON "support" ("issue");

CREATE INDEX ON "support" ("create_date");

CREATE INDEX ON "support" ("end_date");

CREATE INDEX ON "product" ("id");

CREATE INDEX ON "product" ("type");

CREATE INDEX ON "product" ("code");

CREATE INDEX ON "product" ("name");

CREATE INDEX ON "product" ("create_date");

CREATE INDEX ON "product" ("end_date");

CREATE INDEX ON "product" ("status");

CREATE INDEX ON "product" ("region_id");

CREATE INDEX ON "region" ("id");

CREATE INDEX ON "region" ("name");

CREATE INDEX ON "region" ("create_date");

CREATE INDEX ON "region" ("status");

CREATE INDEX ON "region" ("city");

CREATE INDEX ON "region" ("country_code");

CREATE INDEX ON "promotion" ("type");

CREATE INDEX ON "promotion" ("create_date");

CREATE INDEX ON "promotion" ("start_date");

CREATE INDEX ON "promotion" ("end_date");

CREATE INDEX ON "promotion" ("status");

CREATE INDEX ON "promotion" ("region_id");

CREATE INDEX ON "promotion" ("target_product_types");

CREATE INDEX ON "promotion" ("target_product_ids");

CREATE INDEX ON "promotion" ("discount_code");

CREATE INDEX ON "order_group" ("type");

CREATE INDEX ON "order_group" ("code");

CREATE INDEX ON "order_group" ("user_id");

CREATE INDEX ON "order_group" ("create_date");

CREATE INDEX ON "order_group" ("status");

CREATE INDEX ON "order" ("type");

CREATE INDEX ON "order" ("product_type");

CREATE INDEX ON "order" ("code");

CREATE INDEX ON "order" ("user_id");

CREATE INDEX ON "order" ("group_id");

CREATE INDEX ON "order" ("status");

CREATE INDEX ON "order" ("create_date");

CREATE INDEX ON "order" ("start_date");

CREATE INDEX ON "order" ("end_date");

CREATE INDEX ON "order" ("discount_code");

CREATE INDEX ON "order" ("promotion_id");

CREATE INDEX ON "order" ("payment_type");

CREATE INDEX ON "order" ("region_id");

CREATE INDEX ON "order_product" ("order_id");

CREATE INDEX ON "order_product" ("product_id");

CREATE INDEX ON "billing" ("type");

CREATE INDEX ON "billing" ("code");

CREATE INDEX ON "billing" ("user_id");

CREATE INDEX ON "billing" ("order_id");

CREATE INDEX ON "billing" ("create_date");

CREATE INDEX ON "billing" ("end_date");

CREATE INDEX ON "billing" ("status");

CREATE INDEX ON "balance" ("user_id");

CREATE INDEX ON "balance" ("type");

CREATE INDEX ON "balance" ("create_date");

CREATE INDEX ON "balance" ("end_date");

CREATE INDEX ON "balance" ("status");

CREATE INDEX ON "balance" ("balance");

CREATE INDEX ON "compute" ("type");

CREATE INDEX ON "compute" ("name");

CREATE INDEX ON "compute" ("version");

CREATE INDEX ON "compute" ("user_id");

CREATE INDEX ON "compute" ("order_id");

CREATE INDEX ON "compute" ("backend_id");

CREATE INDEX ON "compute" ("create_date");

CREATE INDEX ON "compute" ("end_date");

CREATE INDEX ON "compute" ("status");

CREATE INDEX ON "compute" ("public_ip");

CREATE INDEX ON "compute" ("region_id");

CREATE INDEX ON "session" ("session_id");

CREATE INDEX ON "public_ip" ("type");

CREATE INDEX ON "public_ip" ("version");

CREATE INDEX ON "public_ip" ("status");

CREATE INDEX ON "public_ip" ("mac_addr");

CREATE INDEX ON "public_ip" ("user_id");

CREATE INDEX ON "public_ip" ("compute_id");

CREATE INDEX ON "public_ip" ("create_date");

CREATE INDEX ON "public_ip" ("start_date");

CREATE INDEX ON "public_ip" ("end_date");

CREATE INDEX ON "task" ("type");

CREATE INDEX ON "task" ("action");

CREATE INDEX ON "task" ("user_id");

CREATE INDEX ON "task" ("target_id");

CREATE INDEX ON "task" ("target_entity");

CREATE INDEX ON "task" ("target_time");

CREATE INDEX ON "task" ("target_date");

CREATE INDEX ON "task" ("status");

CREATE INDEX ON "task" ("create_date");

CREATE INDEX ON "task" ("start_date");

CREATE INDEX ON "task" ("end_date");
