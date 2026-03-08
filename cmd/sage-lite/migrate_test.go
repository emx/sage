package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestMigrateOnUpgrade_FirstRun(t *testing.T) {
	// Simulate first run — no version file exists
	tmpDir := t.TempDir()
	origHome := os.Getenv("SAGE_HOME")
	os.Setenv("SAGE_HOME", tmpDir)
	defer os.Setenv("SAGE_HOME", origHome)

	dataDir := filepath.Join(tmpDir, "data")
	os.MkdirAll(dataDir, 0700)

	oldVersion := version
	version = "v2.5.0"
	defer func() { version = oldVersion }()

	migrated, err := migrateOnUpgrade(dataDir)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if migrated {
		t.Error("expected no migration on first run")
	}

	// Version file should be stamped
	vPath := filepath.Join(tmpDir, versionFile)
	data, err := os.ReadFile(vPath)
	if err != nil {
		t.Fatalf("version file not written: %v", err)
	}
	if got := string(data); got != "v2.5.0\n" {
		t.Errorf("version file content = %q, want %q", got, "v2.5.0\n")
	}
}

func TestMigrateOnUpgrade_SameVersion(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("SAGE_HOME")
	os.Setenv("SAGE_HOME", tmpDir)
	defer os.Setenv("SAGE_HOME", origHome)

	dataDir := filepath.Join(tmpDir, "data")
	os.MkdirAll(dataDir, 0700)

	oldVersion := version
	version = "v2.5.0"
	defer func() { version = oldVersion }()

	// Write same version
	os.WriteFile(filepath.Join(tmpDir, versionFile), []byte("v2.5.0\n"), 0600)

	migrated, err := migrateOnUpgrade(dataDir)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if migrated {
		t.Error("should not migrate when version unchanged")
	}
}

func TestMigrateOnUpgrade_VersionChanged(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("SAGE_HOME")
	os.Setenv("SAGE_HOME", tmpDir)
	defer os.Setenv("SAGE_HOME", origHome)

	dataDir := filepath.Join(tmpDir, "data")
	badgerDir := filepath.Join(dataDir, "badger")
	cometDir := filepath.Join(dataDir, "cometbft", "data")
	sqlitePath := filepath.Join(dataDir, "sage.db")

	os.MkdirAll(badgerDir, 0700)
	os.MkdirAll(cometDir, 0700)

	// Create fake SQLite DB
	os.WriteFile(sqlitePath, []byte("fake-sqlite-data"), 0600)
	// Create fake BadgerDB files
	os.WriteFile(filepath.Join(badgerDir, "000001.vlog"), []byte("badger"), 0600)
	// Create fake CometBFT state DBs
	os.MkdirAll(filepath.Join(cometDir, "blockstore.db"), 0700)
	os.MkdirAll(filepath.Join(cometDir, "state.db"), 0700)
	os.WriteFile(filepath.Join(cometDir, "priv_validator_state.json"), []byte(`{"height":"100"}`), 0600)

	// Write old version
	os.WriteFile(filepath.Join(tmpDir, versionFile), []byte("v2.4.0\n"), 0600)

	oldVersion := version
	version = "v2.5.0"
	defer func() { version = oldVersion }()

	migrated, err := migrateOnUpgrade(dataDir)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !migrated {
		t.Error("expected migration when version changed")
	}

	// Verify backup was created
	backupDir := filepath.Join(tmpDir, "backups")
	entries, _ := os.ReadDir(backupDir)
	if len(entries) == 0 {
		t.Error("no backup file created")
	}
	// Verify backup contains the original data
	for _, e := range entries {
		data, _ := os.ReadFile(filepath.Join(backupDir, e.Name()))
		if string(data) != "fake-sqlite-data" {
			t.Error("backup doesn't contain original SQLite data")
		}
	}

	// Verify BadgerDB was wiped
	badgerEntries, _ := os.ReadDir(badgerDir)
	if len(badgerEntries) != 0 {
		t.Errorf("badger dir should be empty, has %d entries", len(badgerEntries))
	}

	// Verify CometBFT block DBs were removed
	if _, err := os.Stat(filepath.Join(cometDir, "blockstore.db")); !os.IsNotExist(err) {
		t.Error("blockstore.db should have been removed")
	}
	if _, err := os.Stat(filepath.Join(cometDir, "state.db")); !os.IsNotExist(err) {
		t.Error("state.db should have been removed")
	}

	// Verify validator state was reset
	pvState, _ := os.ReadFile(filepath.Join(cometDir, "priv_validator_state.json"))
	if string(pvState) != `{"height":"0","round":0,"step":0}` {
		t.Errorf("validator state not reset: %s", pvState)
	}

	// Verify new version stamped
	vData, _ := os.ReadFile(filepath.Join(tmpDir, versionFile))
	if string(vData) != "v2.5.0\n" {
		t.Errorf("version file = %q, want v2.5.0", vData)
	}

	// Verify SQLite was NOT touched
	sqlData, _ := os.ReadFile(sqlitePath)
	if string(sqlData) != "fake-sqlite-data" {
		t.Error("SQLite should be preserved during migration")
	}
}

func TestMigrateOnUpgrade_DevVersion(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("SAGE_HOME")
	os.Setenv("SAGE_HOME", tmpDir)
	defer os.Setenv("SAGE_HOME", origHome)

	dataDir := filepath.Join(tmpDir, "data")
	os.MkdirAll(dataDir, 0700)

	oldVersion := version
	version = "dev"
	defer func() { version = oldVersion }()

	// Write any version — dev builds should skip
	os.WriteFile(filepath.Join(tmpDir, versionFile), []byte("v2.4.0\n"), 0600)

	migrated, err := migrateOnUpgrade(dataDir)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if migrated {
		t.Error("dev builds should skip migration")
	}
}
