package middleware

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// ProblemDetails represents an RFC 7807 error response.
type ProblemDetails struct {
	Type     string `json:"type"`
	Title    string `json:"title"`
	Status   int    `json:"status"`
	Detail   string `json:"detail"`
	Instance string `json:"instance,omitempty"`
}

// writeProblem sends an RFC 7807 Problem Details JSON response.
func writeProblem(w http.ResponseWriter, status int, title, detail string) {
	problem := ProblemDetails{
		Type:   fmt.Sprintf("https://sage.dev/errors/%d", status),
		Title:  title,
		Status: status,
		Detail: detail,
	}
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(problem)
}
