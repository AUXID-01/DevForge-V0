# disfluency_module/config.py

# Context for streaming
CONTEXT_SIZE = 30

# Pattern-based repetition (always on, fast)
WINDOWED_BIGRAM_WINDOW = 6

# Semantic repetition (optional, heavier)
ENABLE_SEMANTIC_DETECTION = False  # set True to enable
SEMANTIC_SIMILARITY_THRESHOLD = 0.85
SEMANTIC_NGRAM_SIZE = 3  # trigrams

# Adaptive mode: only use semantic if pattern-based didn't clean much
ENABLE_ADAPTIVE_SEMANTIC = True
ADAPTIVE_CLEANUP_THRESHOLD = 0.15  # if we removed < 15% of tokens, try semantic

# Paths
ENGLISH_FILLERS_PATH = "data/filler_lists/english_fillers.txt"
HINGLISH_FILLERS_PATH = "data/filler_lists/hinglish_fillers.txt"
