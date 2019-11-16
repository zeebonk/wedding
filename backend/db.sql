-- Table: public."Image"

-- DROP TABLE public."Image";

CREATE TABLE public."Image"
(
    code integer NOT NULL,
    src text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Image_pkey" PRIMARY KEY (code)
)

TABLESPACE pg_default;

ALTER TABLE public."Image"
    OWNER to postgres;
