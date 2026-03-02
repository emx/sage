package middleware

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"
	"time"

	"github.com/rs/zerolog/log"
)

// RequestLogger is a chi middleware that logs every request with zerolog.
// It records method, path, status code, duration, agent ID, and a generated
// request ID. The request ID is also set in the X-Request-ID response header.
func RequestLogger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// Generate a request ID.
		reqID := generateRequestID()
		w.Header().Set("X-Request-ID", reqID)

		// Wrap the ResponseWriter to capture the status code.
		ww := &statusWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(ww, r)

		duration := time.Since(start)
		agentID := ContextAgentID(r.Context())

		logger := log.With().
			Str("request_id", reqID).
			Str("method", r.Method).
			Str("path", r.URL.Path).
			Int("status", ww.status).
			Dur("duration", duration).
			Logger()

		if agentID != "" {
			logger = logger.With().Str("agent_id", agentID).Logger()
		}

		if ww.status >= 500 {
			logger.Error().Msg("request completed")
		} else if ww.status >= 400 {
			logger.Warn().Msg("request completed")
		} else {
			logger.Info().Msg("request completed")
		}
	})
}

// statusWriter wraps http.ResponseWriter to capture the response status code.
type statusWriter struct {
	http.ResponseWriter
	status      int
	wroteHeader bool
}

func (w *statusWriter) WriteHeader(code int) {
	if !w.wroteHeader {
		w.status = code
		w.wroteHeader = true
	}
	w.ResponseWriter.WriteHeader(code)
}

func (w *statusWriter) Write(b []byte) (int, error) {
	if !w.wroteHeader {
		w.wroteHeader = true
	}
	return w.ResponseWriter.Write(b)
}

// generateRequestID returns a random 16-byte hex string.
func generateRequestID() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}
