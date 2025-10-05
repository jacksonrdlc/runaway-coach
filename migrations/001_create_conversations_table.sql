-- Create conversations table for chat history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    context JSONB DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index on user_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Index on updated_at for sorting recent conversations
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own conversations
CREATE POLICY "Users can access own conversations"
    ON conversations
    FOR ALL
    USING (user_id = auth.uid());

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at on row update
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Stores chat conversation history between users and the running coach AI';
COMMENT ON COLUMN conversations.id IS 'Unique conversation identifier';
COMMENT ON COLUMN conversations.user_id IS 'User ID from auth.users';
COMMENT ON COLUMN conversations.messages IS 'Array of chat messages in JSON format with role and content';
COMMENT ON COLUMN conversations.context IS 'Optional context data like recent activities, goals, profile info';
COMMENT ON COLUMN conversations.created_at IS 'When the conversation was started';
COMMENT ON COLUMN conversations.updated_at IS 'Last time a message was added to the conversation';
