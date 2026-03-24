<p align="center">
<img src="https://img.shields.io/badge/disclosure-public-red?style=for-the-badge" alt="Vulnerability Disclosure">
<a href="https://www.npmjs.com/package/@aisuite/chub"><img src="https://img.shields.io/badge/chub-v0.1.3-orange?style=for-the-badge" alt="Affected Version"></a>
<a href="RESULTS.md"><img src="https://img.shields.io/badge/tests-240%20isolated%20runs-blue?style=for-the-badge" alt="Tests"></a>
<a href="REPRODUCE.md"><img src="https://img.shields.io/badge/reproducible-Docker-blue?style=for-the-badge" alt="Reproducible"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"></a>
</p>

# Context Hub Supply Chain PoC

**Zero-sanitization vulnerability in [Context Hub](https://github.com/andrewyng/context-hub) (`@aisuite/chub` v0.1.3) enables silent dependency injection through the MCP documentation pipeline.**

**References:** [CWE-94](https://cwe.mitre.org/data/definitions/94.html) (Code Injection) | [CWE-829](https://cwe.mitre.org/data/definitions/829.html) (Untrusted Control Sphere) | [CWE-345](https://cwe.mitre.org/data/definitions/345.html) (Insufficient Verification of Data Authenticity) | [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) (Prompt Injection)

> **Full write-up:** [Stack Overflow for AI Agents Sounds Great - Until Someone Poisons the Well](article.html)

## TL;DR

We created realistic poisoned docs containing fake dependencies (`plaid-link-verify`, `stripe-checkout-guard`) and served them through a local chub MCP server inside isolated Docker containers. No poisoned content was uploaded to Context Hub's registry - we ran `chub build` locally and configured the MCP server to serve pre-built output from disk. From the agent's perspective, the experience is identical to fetching docs from the live registry.

When AI coding assistants fetched the docs, **Haiku silently wrote the fake package into `requirements.txt` in 100% of runs - without ever mentioning it in its text output.** A developer reading the assistant's response would see nothing suspicious, but their project is poisoned.

240 isolated runs. 3 models. 4 effort levels. 2 APIs. 0 contamination.

### What it looks like

The generated code silently imports the fake dependency alongside legitimate modules:

![Generated app.py with injected dependency](assets/app-py-deps.png)

The agent also modifies `CLAUDE.md` to embed the fake package as a "project standard":

![CLAUDE.md after attack](assets/claude-md.png)

## Results

These tables show Plaid Link results (120 isolated runs). See [RESULTS.md](RESULTS.md) for full data including Stripe Checkout (240 total runs).

### Silent Dependency Poisoning (requirements.txt)

| Effort | Haiku | Sonnet | Opus |
|--------|-------|--------|------|
| Low | **100%** | **60%** | 0% |
| Medium | **100%** | **70%** | 0% |
| High | **100%** | **40%** | 0% |
| Max | **100%** | **40%** | 0% |

Haiku never warned about the fake dependency (0/40). Sonnet warned in 48% of runs (19/40) but still poisoned requirements.txt in 53% overall. Opus warned in 75% of runs (30/40) and never poisoned requirements.txt or code.

### CLAUDE.md Persistence (project config backdoor)

| Effort | Haiku | Sonnet | Opus |
|--------|-------|--------|------|
| Low | **90%** | **70%** | 0% |
| Medium | **80%** | **70%** | 0% |
| High | **90%** | **40%** | 0% |
| Max | **90%** | **50%** | 0% |

Haiku modifies the project's `CLAUDE.md` to include the fake dependency as a "project standard" in 88% of runs (35/40). This file gets committed to git - every future developer who clones the repo inherits the poisoned config.

## Attack Chain

```mermaid
flowchart LR
    A["Attacker\nsubmits PR"] -->|"No identity\nverification"| B["Maintainer\nmerges PR"]
    B -->|"No content\nsanitization"| C["Doc on CDN\n(no integrity check)"]
    C -->|"MCP serves\nraw content"| D["Agent context\nwindow"]
    D -->|"Agent acts on\nuntrusted content"| E["Developer\nworkstation"]

    style A fill:#111,stroke:#333,color:#f0f0f0
    style B fill:#161616,stroke:#333,color:#888
    style C fill:#161616,stroke:#333,color:#888
    style D fill:#161616,stroke:#333,color:#888
    style E fill:#111,stroke:#333,color:#f0f0f0
```

## Threat Model

| | |
|---|---|
| **Attacker** | Anyone who can submit a PR to Context Hub's doc registry |
| **Attack surface** | Community docs flowing from GitHub PR to CDN to MCP to agent context |
| **Trust boundary** | Untrusted contributor content treated as authoritative API documentation |
| **Prerequisite** | One merged PR containing a poisoned document |
| **Impact** | Arbitrary code execution via dependency injection + pip post-install hooks |

## Key Findings

1. **Haiku poisoning is fully silent.** 0/80 Haiku runs across both APIs mentioned the fake dependency in the response. The model writes to disk without telling. Sonnet warned in 48% of runs but still poisoned requirements.txt in 35-53% of runs. Opus warned in 23-75% of runs and never poisoned requirements.txt or code.

2. **Haiku is 100% exploitable at every effort level.** Effort-independent on both APIs. The weakest model in the family never catches the fake dependency.

3. **Opus resists code poisoning but not config poisoning.** Opus never wrote the fake dependency to requirements.txt or Python code (0/80 across both APIs). But on Stripe, Opus modified CLAUDE.md in 38% of runs, documenting the canary as a project dependency without installing it.

4. **CLAUDE.md persistence creates a supply chain vector.** Modified config files get committed to git, poisoning every developer who clones the repo and every future AI session in that project. This works across all models (Haiku 88-90%, Sonnet 58%, Opus 0-38%).

5. **API familiarity matters.** Stripe (well-known): models detect fake packages via training data. Plaid (less known): models cannot verify and accept the fake dependency without question.

6. **This is a category-wide problem.** Context7 had [ContextCrush](https://noma.security/blog/contextcrush-context7-the-mcp-server-vulnerability/) (Feb 2026). Context Hub has this. Any tool injecting unsanitized external content into agent context is vulnerable.

## Source Code Findings

Zero sanitization across the entire pipeline:

- `annotations.js` - `writeFileSync` with raw content, no filtering
- `build.js` - no content scanning, no unicode normalization
- `cache.js` - CDN fetch with zero hash/signature verification
- `source: official` in frontmatter - self-declared, not verified

## Disclosure

Context Hub has no `SECURITY.md`. There is no documented way to responsibly disclose a vulnerability - no security contact, no PGP key, no disclosure policy. Community members found the vulnerabilities anyway and filed them as regular issues and PRs. None were reviewed.

![Open security PRs with zero reviews](assets/chub-open-security-issues.png)

| Date | Event |
|------|-------|
| 2026-03-12 | [Issue #74](https://github.com/andrewyng/context-hub/issues/74) filed by [@bjorkbjork](https://github.com/bjorkbjork) reporting 4 security vulnerabilities including CDN integrity, self-declared source verification, and annotation injection |
| 2026-03-12 | Issue #74 assigned internally to core team member - zero follow-up |
| 2026-03-17 | [PR #125](https://github.com/andrewyng/context-hub/pull/125) filed by [@hobostay](https://github.com/hobostay) adding content integrity verification - zero reviews |
| 2026-03-12 to 03-20 | Additional security PRs ([#69](https://github.com/andrewyng/context-hub/pull/69), [#81](https://github.com/andrewyng/context-hub/pull/81)) filed by community - zero reviews |
| 2026-03-20 to 03-23 | Our independent audit confirms and quantifies the vulnerabilities with 240 isolated Docker runs |
| 2026-03-23 | Public disclosure |

**Note:** We did not file issue #74. Our audit independently discovered and quantified these vulnerabilities. Issue #74 and PRs #69, #81, #125 are cited as prior art demonstrating the community has flagged these issues with zero maintainer engagement.

## Escalation

Once the fake package is in `requirements.txt`, a standard `pip install -r requirements.txt` gives the attacker arbitrary code execution via `setup.py` post-install hooks. This is not a sandbox - pip runs unrestricted Python with the developer's full permissions.

From that single entry point, the attacker can:

- **Exfiltrate data.** Read and send environment variables, API keys, AWS credentials, SSH keys, `.env` files, or source code to an attacker-controlled server.
- **Install a persistent backdoor.** Reverse shell, cron job, modified shell profile, or background process that survives package uninstallation.
- **Poison the chub registry.** Modify `~/.chub/config.yaml` to add an attacker-controlled doc source. All future chub queries across every library now include attacker content. Survives `chub cache clear` because config is not cache.
- **Propagate through git.** The CLAUDE.md modification gets committed. Every developer who clones the repo inherits the poisoned config. If they run the same workflow, the attack repeats on their machine.

These are not mutually exclusive. A single post-install hook can do all of them in under a second. We did not create or register a malicious package.

## Repository Structure

```
.
|-- README.md                    # This file
|-- RESULTS.md                   # Full dataset with per-run breakdowns
|-- REPRODUCE.md                 # Docker-based reproduction guide
|-- alternatives-comparison.md   # Context7, LAP, GitMCP, Docfork comparison
|-- article.html                 # Full write-up
|-- docker/
|   |-- Dockerfile               # Isolated test environment
|   |-- run_isolated.ps1         # PowerShell runner (Windows/macOS/Linux via pwsh)
|   |-- seed-claude.md           # Minimal CLAUDE.md seeded into each run
|   |-- plaid-doc/               # Poisoned Plaid Link doc (canary: plaid-link-verify)
|   |   `-- plaid/link/DOC.md
|   `-- stripe-doc/              # Poisoned Stripe Checkout doc (canary: stripe-checkout-guard)
|       `-- stripe/checkout/DOC.md
`-- results/
    |-- plaid-isolated/          # 120 Plaid runs: JSON + session transcripts + project files
    `-- stripe-isolated/         # 120 Stripe runs: JSON + session transcripts + project files
```

## Reproducing the Results

See [REPRODUCE.md](REPRODUCE.md) for the full Docker-based reproduction guide.

Quick start:
```bash
# Plaid (default)
docker build --build-arg DOC_DIR=plaid-doc -t plaid-bench docker/
docker run -d --name plaid-runner plaid-bench sleep infinity
docker exec -it plaid-runner claude login

# Stripe
docker build --build-arg DOC_DIR=stripe-doc -t stripe-bench docker/
docker run -d --name stripe-runner stripe-bench sleep infinity
docker exec -it stripe-runner claude login

# Then run the test matrix from the host (see REPRODUCE.md)
```

## Limitations

1. Only Claude models tested. GPT-4, Gemini, Llama may differ.
2. 10 runs per cell - sufficient for trends, not for narrow confidence intervals.
3. Tests used `--permission-mode bypassPermissions`. Real agents may prompt for confirmation.
4. Local doc source, not CDN. CDN path requires a merged malicious PR.
5. No real malicious package was registered on PyPI.

## Related Work

- [ContextCrush](https://noma.security/blog/contextcrush-context7-the-mcp-server-vulnerability/) (Noma Security, Feb 2026) - same class of attack against Context7
- [Morris II](https://sites.google.com/view/compromptmized) (Cohen, Bitton, Nassi) - self-replicating prompts in AI agents
- [Promptware Kill Chain](https://arxiv.org/abs/2601.09625) (Nassi, Schneier et al.) - multi-stage LLM attack taxonomy
- [MCP Tool Poisoning](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) (Invariant Labs) - cross-server tool manipulation

## License

MIT

## Disclosure

This research was conducted by Mickey Shmueli, the developer of [LAP](https://github.com/Lap-Platform), an open-source alternative to Context Hub. LAP uses deterministic compilation from official API specs, with no community-contributed content in the pipeline. This audit was motivated by a genuine security concern about unsanitized content pipelines - a class of vulnerability that affects any tool in this space that accepts unverified community contributions. The findings stand on their own: 240 isolated Docker runs, deterministic detection, fully reproducible.

## Disclaimer

This PoC is for educational and security research purposes only. All tests performed locally in isolated Docker containers. No malicious content was submitted to the Context Hub repository. All canary package names verified non-existent on PyPI before testing.

These vulnerabilities were independently reported by community members in [issue #74](https://github.com/andrewyng/context-hub/issues/74) (March 12) and [PR #125](https://github.com/andrewyng/context-hub/pull/125) (March 17). Both received zero maintainer response.
