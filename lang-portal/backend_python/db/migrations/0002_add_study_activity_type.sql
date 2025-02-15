-- Add type column to study_activities table
ALTER TABLE study_activities ADD COLUMN type TEXT NOT NULL DEFAULT 'ja_to_en';

-- Update existing records with appropriate types
UPDATE study_activities 
SET type = 'ja_to_en' 
WHERE name = 'Vocabulary Quiz';

UPDATE study_activities 
SET type = 'en_to_ja' 
WHERE name = 'Writing Practice';

-- Remove the default constraint after migration
-- Note: SQLite doesn't support removing default constraints, 
-- but new records will require the type field anyway due to the model definition 