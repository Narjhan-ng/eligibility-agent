-- ======================================
-- Eligibility Agent - Conversation Memory Database
-- ======================================
--
-- This schema stores conversation history to enable:
-- - Multi-turn dialogues with context awareness
-- - Session persistence across page reloads
-- - Conversation analytics
--
-- Created: Day 6 - Conversation Memory Implementation
-- ======================================

-- === SESSIONS TABLE ===
-- Tracks user sessions with metadata
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session identification
    session_key VARCHAR(255) UNIQUE NOT NULL,  -- Client-generated session ID

    -- Metadata
    user_identifier VARCHAR(255),  -- Optional: email, user_id, etc.
    user_agent TEXT,               -- Browser/client info
    ip_address INET,               -- Client IP for analytics

    -- Context
    initial_query TEXT,            -- First question asked
    customer_profile JSONB,        -- Customer data if provided

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, abandoned

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '24 hours',

    -- Indexes for fast lookups
    INDEX idx_sessions_session_key (session_key),
    INDEX idx_sessions_created_at (created_at),
    INDEX idx_sessions_status (status)
);

-- === MESSAGES TABLE ===
-- Stores all messages in conversations (both user and agent)
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,

    -- Session relationship
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Message content
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system', 'tool'
    content TEXT NOT NULL,       -- The actual message text

    -- Metadata
    message_metadata JSONB,      -- Additional context (tools called, processing time, etc.)

    -- Tool usage (if role = 'tool')
    tool_name VARCHAR(100),      -- Name of tool called
    tool_input JSONB,            -- Tool input parameters
    tool_output JSONB,           -- Tool result

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_messages_session_id (session_id),
    INDEX idx_messages_created_at (created_at),
    INDEX idx_messages_role (role)
);

-- === CONVERSATION ANALYTICS VIEW ===
-- Useful for understanding usage patterns
CREATE OR REPLACE VIEW conversation_analytics AS
SELECT
    s.id as session_id,
    s.session_key,
    s.status,
    s.created_at,
    s.updated_at,
    COUNT(m.id) as message_count,
    COUNT(CASE WHEN m.role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN m.role = 'assistant' THEN 1 END) as assistant_messages,
    COUNT(CASE WHEN m.role = 'tool' THEN 1 END) as tool_calls,
    MAX(m.created_at) as last_message_at,
    EXTRACT(EPOCH FROM (MAX(m.created_at) - s.created_at)) as duration_seconds
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY s.id, s.session_key, s.status, s.created_at, s.updated_at;

-- === AUTOMATIC UPDATED_AT TRIGGER ===
-- Updates the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- === SESSION CLEANUP FUNCTION ===
-- Remove expired sessions (can be called by cron job)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at < NOW()
    AND status != 'completed';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- === COMMENTS FOR DOCUMENTATION ===
COMMENT ON TABLE sessions IS 'User conversation sessions with metadata';
COMMENT ON TABLE messages IS 'All messages (user, assistant, tool) in conversations';
COMMENT ON VIEW conversation_analytics IS 'Aggregated conversation metrics for analytics';
COMMENT ON FUNCTION cleanup_expired_sessions() IS 'Removes expired sessions (call from cron)';

-- === SAMPLE QUERIES ===
--
-- Get conversation history for a session:
-- SELECT role, content, created_at
-- FROM messages
-- WHERE session_id = 'xxx'
-- ORDER BY created_at ASC;
--
-- Get active sessions:
-- SELECT * FROM sessions WHERE status = 'active' AND expires_at > NOW();
--
-- Get conversation analytics:
-- SELECT * FROM conversation_analytics ORDER BY created_at DESC LIMIT 10;
