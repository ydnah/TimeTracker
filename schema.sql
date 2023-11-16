CREATE TABLE "time" (
    "id" INTEGER PRIMARY KEY,
    "application" TEXT NOT NULL,
    "user" TEXT NOT NULL,
    "datetime" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "duration" NUMERIC NOT NULL CHECK("duration" != 0), 
    "type" TEXT CHECK("type" in ('automatic', 'manual'))
);