CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    recipe_name TEXT UNIQUE,
    description TEXT,
    ingredients JSONB,
    instructions TEXT,
    total_time INT,
    servings TEXT,
    author TEXT,
    host TEXT,
    recipe_language TEXT,
    nutrition_data JSONB,
    recipe_url TEXT UNIQUE,
    image_url TEXT,
    scraped boolean DEFAULT true,
    active boolean DEFAULT true
);

-- Table: public.bbc_good_food_recipe_links
-- DROP TABLE IF EXISTS public.bbc_good_food_recipe_links;
CREATE TABLE IF NOT EXISTS public.bbc_good_food_recipe_links (
    id integer NOT NULL DEFAULT nextval('bbc_good_food_recipe_links_id_seq' :: regclass),
    url text COLLATE pg_catalog."default",
    scraped boolean DEFAULT false,
    CONSTRAINT bbc_good_food_recipe_links_pkey PRIMARY KEY (id),
    CONSTRAINT bbc_good_food_recipe_links_url_key UNIQUE (url)
) TABLESPACE pg_default;

ALTER TABLE
    IF EXISTS public.bbc_good_food_recipe_links OWNER to postgres;

-- Table: public.bbc_good_food_category_links
-- DROP TABLE IF EXISTS public.bbc_good_food_category_links;
CREATE TABLE IF NOT EXISTS public.bbc_good_food_category_links (
    id integer NOT NULL DEFAULT nextval('bbc_good_food_category_links_id_seq' :: regclass),
    url text COLLATE pg_catalog."default",
    scraped boolean DEFAULT false,
    CONSTRAINT bbc_good_food_category_links_pkey PRIMARY KEY (id),
    CONSTRAINT bbc_good_food_category_links_url_key UNIQUE (url)
) TABLESPACE pg_default;

ALTER TABLE
    IF EXISTS public.bbc_good_food_category_links OWNER to postgres;