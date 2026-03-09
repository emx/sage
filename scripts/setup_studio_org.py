#!/usr/bin/env python3
"""Set up Dhillon's studio org with RBAC for laptop + Mac Mini voice agent.

Org: "l33tdawg Studio"
  - Department: command (laptop — full admin)
  - Department: voice (Mac Mini — scoped access)

Shared domains: general, calendar, projects
Private domains: personal, reflection (laptop only)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python", "src"))

from sage_sdk import AgentIdentity, SageClient
from sage_sdk.exceptions import SageAPIError, SageAuthError

SAGE_URL = os.environ.get("SAGE_URL", "http://localhost:8080")

# Load real keys
LAPTOP_KEY = os.path.expanduser("~/.sage/agent.key")
MACMINI_KEY = os.environ.get("MACMINI_KEY_PATH", "/tmp/macmini-agent.key")


def main():
    laptop = AgentIdentity.from_file(LAPTOP_KEY)
    macmini = AgentIdentity.from_file(MACMINI_KEY)

    print(f"Laptop agent:   {laptop.agent_id[:16]}...")
    print(f"Mac Mini agent: {macmini.agent_id[:16]}...")
    print()

    with SageClient(base_url=SAGE_URL, identity=laptop) as client:

        # 1. Register org
        print("[1/6] Registering organization: l33tdawg Studio")
        try:
            org = client.register_org(
                name="l33tdawg Studio",
                description="Dhillon's personal AI infrastructure — laptop + Mac Mini voice station",
            )
            org_id = org["org_id"]
            print(f"       org_id: {org_id}")
            print(f"       tx_hash: {org['tx_hash']}")
        except SageAPIError as e:
            if "already exists" in str(e.detail).lower():
                print("       Org already exists, continuing...")
                # Need to compute org_id deterministically
                import hashlib
                pub_bytes = bytes.fromhex(laptop.agent_id)
                org_id = hashlib.sha256(pub_bytes + b"l33tdawg Studio").hexdigest()[:32]
                print(f"       org_id (computed): {org_id}")
            else:
                raise
        print()

        # 2. Create departments
        print("[2/6] Creating departments...")

        try:
            cmd_dept = client.register_dept(
                org_id=org_id,
                name="command",
                description="Primary command node — laptop, full admin access",
            )
            cmd_dept_id = cmd_dept["dept_id"]
            print(f"       command dept_id: {cmd_dept_id}")
        except SageAPIError as e:
            if "already exists" in str(e.detail).lower():
                import hashlib
                cmd_dept_id = hashlib.sha256((org_id + "command").encode()).hexdigest()[:16]
                print(f"       command dept already exists: {cmd_dept_id}")
            else:
                raise

        try:
            voice_dept = client.register_dept(
                org_id=org_id,
                name="voice",
                description="Voice interface — Mac Mini, scoped read access",
            )
            voice_dept_id = voice_dept["dept_id"]
            print(f"       voice dept_id: {voice_dept_id}")
        except SageAPIError as e:
            if "already exists" in str(e.detail).lower():
                import hashlib
                voice_dept_id = hashlib.sha256((org_id + "voice").encode()).hexdigest()[:16]
                print(f"       voice dept already exists: {voice_dept_id}")
            else:
                raise
        print()

        # 3. Add members with clearance
        print("[3/6] Adding members...")

        # Laptop = admin (clearance 4) in both departments
        try:
            client.add_dept_member(org_id=org_id, dept_id=cmd_dept_id,
                                   agent_id=laptop.agent_id, clearance=4, role="admin")
            print(f"       Laptop -> command (clearance=4, admin)")
        except SageAPIError:
            print(f"       Laptop already in command dept")

        try:
            client.add_dept_member(org_id=org_id, dept_id=voice_dept_id,
                                   agent_id=laptop.agent_id, clearance=4, role="admin")
            print(f"       Laptop -> voice (clearance=4, admin)")
        except SageAPIError:
            print(f"       Laptop already in voice dept")

        # Mac Mini = member (clearance 1) in voice department only
        try:
            client.add_org_member(org_id=org_id, agent_id=macmini.agent_id, clearance=1)
            print(f"       Mac Mini added to org (clearance=1)")
        except SageAPIError:
            print(f"       Mac Mini already in org")

        try:
            client.add_dept_member(org_id=org_id, dept_id=voice_dept_id,
                                   agent_id=macmini.agent_id, clearance=1, role="member")
            print(f"       Mac Mini -> voice (clearance=1, member)")
        except SageAPIError:
            print(f"       Mac Mini already in voice dept")
        print()

        # 4. Register shared domains
        print("[4/6] Registering domains...")
        for domain in ["general", "calendar", "projects", "voice", "personal", "reflection"]:
            try:
                client.register_domain(name=domain, description=f"{domain} knowledge domain")
                print(f"       Registered: {domain}")
            except SageAPIError:
                print(f"       {domain} already exists")
        print()

        # 5. Grant domain access
        print("[5/6] Granting domain access...")

        # Mac Mini gets read access to shared domains
        for domain in ["general", "calendar", "projects", "voice"]:
            try:
                client.grant_access(
                    grantee_id=macmini.agent_id,
                    domain=domain,
                    level=1 if domain != "voice" else 2,  # voice dept gets read+write on voice domain
                )
                level = "read+write" if domain == "voice" else "read"
                print(f"       Mac Mini -> {domain} ({level})")
            except SageAPIError:
                print(f"       Mac Mini already has {domain} access")

        # Mac Mini does NOT get access to personal or reflection domains
        print(f"       Mac Mini: NO access to personal, reflection (private to laptop)")
        print()

        # 6. Verify
        print("[6/6] Verifying org structure...")
        try:
            members = client.list_org_members(org_id)
            print(f"       Org members: {len(members)}")
            for m in members:
                print(f"         - {m['agent_id'][:16]}... role={m.get('role', 'member')} clearance={m.get('clearance', '?')}")
        except SageAPIError as e:
            print(f"       Could not list members: {e.detail}")

        try:
            voice_members = client.list_dept_members(org_id, voice_dept_id)
            print(f"       Voice dept members: {len(voice_members)}")
        except SageAPIError as e:
            print(f"       Could not list voice dept: {e.detail}")

    print()
    print("Done! RBAC structure is on-chain.")
    print(f"  Org: l33tdawg Studio ({org_id})")
    print(f"  Laptop: admin, all domains, clearance 4")
    print(f"  Mac Mini: voice member, shared domains only, clearance 1")


if __name__ == "__main__":
    try:
        main()
    except SageAuthError as e:
        print(f"\nAuth error: {e}", file=sys.stderr)
        sys.exit(1)
    except SageAPIError as e:
        print(f"\nAPI error (HTTP {e.status_code}): {e.detail}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
