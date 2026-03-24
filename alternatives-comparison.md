## Alternative Approaches

This section compares tools that address the same problem space as Context Hub -- delivering documentation into AI agent context windows -- with a focus on the security properties relevant to the vulnerabilities documented in this audit: content sanitization, source verification, and injection resistance.

This is a source-based comparison of publicly documented behavior and disclosures, not an independent security audit of the other tools listed here.

### Comparison Table

| Property | Context Hub | Context7 | LAP | GitMCP | Docfork | llms.txt |
|---|---|---|---|---|---|---|
| **Content format** | Free-form Markdown with YAML frontmatter | Free-form documentation + custom AI rules | Structured @directive grammar (compiled from OpenAPI, GraphQL, etc.) | llms.txt / README from GitHub repos | Pre-chunked documentation | Plain Markdown (proposed convention) |
| **Sanitization** | None. `writeFileSync` with no validation. Annotations injected raw into agent context. | None at time of ContextCrush disclosure (Feb 2026). Patched Feb 23, 2026 with "rule sanitization and guardrails" -- implementation details not public. | Structural. Compiler strips free-form prose during compilation; output is constrained to typed directives (`@route`, `@param`, `enum()`, `str()`, etc.). | None documented. Serves raw repository content (llms.txt, README). | Not documented. | None. Raw Markdown served as-is. |
| **Source verification** | None. `source: official/maintainer` is self-declared metadata with no verification mechanism. | None documented. Community-contributed libraries are accepted without domain ownership proof. A "Report" button exists for flagging suspicious content. | DNS TXT record verification. Publishers must add a platform-generated TXT record to their domain's DNS to claim a provider namespace. Community-submitted specs are visually distinguished from verified publisher specs. | Implicit -- content comes from the GitHub repository itself. No independent verification of content integrity. | Not documented. | None. Any website can publish an llms.txt file. |
| **Community input model** | Open PRs to a public GitHub repo. Human review only. No automated scanning for injection patterns. | Open submissions via dashboard. Custom AI rules were served verbatim with no filtering (pre-patch). | Two tiers: verified publishers (DNS-proven domain owners) publish official specs; community members can submit specs that are labeled as community-contributed. All specs are compiled through the same deterministic compiler. | No community contribution layer. Content is whatever the repository owner publishes. | Community library submissions; "Cabinets" feature restricts agent to a declared stack. | No community layer. Site owner publishes their own file. |
| **MCP support** | No (CLI-based: `chub get`) | Yes (primary interface) | No (CLI-based: `lapsh get`; integrates with MCP-compatible tools via SDKs) | Yes (primary interface) | Yes (primary interface) | No (static file convention) |
| **Known vulnerabilities** | Zero-day: zero sanitization across entire pipeline (this audit). Annotation worm, data exfiltration, RCE via doc content. Issue #74 was reported on Mar 12, 2026, with no public maintainer response noted through Mar 24, 2026. | ContextCrush (CVE pending): custom rules served verbatim with no sanitization, enabling credential theft and file deletion via injected AI instructions. Disclosed Feb 18, patched Feb 23, 2026. | No public vulnerability disclosures were found in the sources reviewed for this comparison. | No public vulnerability disclosures were found in the sources reviewed for this comparison, but serving raw repo content without sanitization carries inherent injection risk for repos with untrusted contributors. | No public vulnerability disclosures were found in the sources reviewed for this comparison. | Not a tool per se; inherits whatever security the consuming tool provides. |

### Tool-by-Tool Analysis

#### Context7 (Upstash)

Context7 is an MCP server that indexes documentation for thousands of libraries and serves version-specific docs and code examples to AI coding assistants. It is one of the most widely adopted tools in this category.

**Security-relevant properties:**

- The ContextCrush vulnerability (disclosed Feb 2026 by Noma Security) demonstrated that Context7's "Custom Rules" feature served attacker-controlled content verbatim through the MCP server, with no sanitization, content filtering, or distinction from legitimate documentation. Researchers demonstrated credential theft, data exfiltration, and destructive file operations through this vector.
- Upstash publicly disclosed a fix on Feb 23, 2026. The fix adds "rule sanitization and guardrails," though the specific implementation has not been publicly documented.
- Context7's own documentation states: "Context7 projects are community-contributed and while we strive to maintain high quality, we cannot guarantee the accuracy, completeness, or security of all library documentation."
- The core architecture -- fetching external documentation and injecting it into AI context -- shares the same fundamental attack surface as Context Hub. Content from external sources passes through an MCP channel that AI agents treat as authoritative.

**Limitations:** The backend (API, parsing engine, crawling engine) is closed-source, making independent security audit of the sanitization fix impossible. The community contribution model does not include domain ownership verification for library publishers.

#### LAP (Lean API Platform)

LAP is a compiler that converts API specifications (OpenAPI, GraphQL, AsyncAPI, Protobuf, Postman, AWS Smithy) into a compact, structured format using @directive syntax. It maintains a registry of more than 1,500 pre-compiled API specs at registry.lap.sh.

**Security-relevant properties:**

- LAP's primary security property is structural: the compilation step transforms free-form API specifications into a constrained grammar of typed directives. Free-form prose, arbitrary Markdown, and natural-language instructions are stripped during compilation. This means the output format has a reduced attack surface for prompt injection compared to free-form Markdown, because the content delivered to agents is constrained to declarations like `@route GET /users`, `@param {id: str(uuid)}`, and `enum(active|inactive|deleted)`.
- Publisher verification uses DNS TXT records -- a mechanism borrowed from email authentication (SPF/DKIM) and SSL certificate validation. Publishers must prove domain ownership before publishing under a provider namespace. This prevents namespace squatting where an attacker publishes specs under a provider name they do not own.
- Community-contributed specs are visually distinguished from verified publisher specs in the registry, giving consumers a trust signal.
- The compilation is deterministic: the same input spec always produces the same output, making it diffable and auditable.

**Limitations:** LAP addresses API specification delivery, not general documentation. It is not a direct replacement for Context Hub or Context7 in use cases that require prose documentation, tutorials, or migration guides. The typed-directive format provides structural resistance to injection, but this has not been independently validated through adversarial security testing (no public pentest results found). The DNS TXT verification proves domain ownership but does not guarantee the spec content itself is safe -- a verified publisher could still publish a malicious spec. LAP does not use MCP natively, though it integrates with MCP-compatible tools.

#### GitMCP

GitMCP is a free, open-source MCP server that turns any public GitHub repository into a documentation source by reading llms.txt, README files, and repository content.

**Security-relevant properties:**

- GitMCP does not store data or require authentication, reducing its own attack surface.
- It respects robots.txt directives, allowing repository owners to opt out.
- Content served is whatever exists in the repository. There is no sanitization layer between the repository content and the AI agent's context window.

**Limitations:** GitMCP inherits the security posture of the source repository. If a repository contains injected content (via a malicious PR, compromised maintainer account, or social engineering), GitMCP will serve that content to AI agents without modification. It provides no content filtering, no source verification beyond GitHub's own access controls, and no injection detection. For repositories with many contributors or permissive merge policies, this is a meaningful risk.

#### Docfork

Docfork is an MCP server indexing thousands of libraries with a "Cabinets" feature that restricts an agent to a declared set of libraries.

**Security-relevant properties:**

- The Cabinets feature provides context isolation: agents are locked to a verified stack, which prevents context poisoning from unrelated libraries. This is a defense-in-depth measure -- it does not prevent injection within an approved library's documentation, but it limits the blast radius.
- Pre-chunked, edge-cached retrieval reduces the window for content tampering during transit.

**Limitations:** No public documentation on content sanitization within the documentation pipeline itself. Cabinets address cross-library contamination but not within-library injection. No public vulnerability disclosures or security audit results found.

#### llms.txt

llms.txt is a proposed convention (not a formal standard) where websites publish a Markdown file at `/llms.txt` summarizing their documentation for AI consumption. It is analogous to robots.txt but for LLM-readable content.

**Security-relevant properties:**

- Content is published by the domain owner, providing implicit source verification (the content comes from the domain it describes).
- The format is intentionally simple, reducing the tooling attack surface.

**Limitations:** llms.txt is a file format convention, not a security mechanism. It provides no sanitization, no content validation, and no injection resistance. The consuming tool is responsible for all security properties. As the llms.txt documentation itself notes, it should not be used as a security mechanism. Any content at that URL is served raw, and prompt injection payloads embedded in an llms.txt file will be delivered unchanged to any AI agent that reads it.

### Summary

No tool in this space has fully solved the content sanitization problem. The approaches fall into three categories:

1. **No sanitization** (Context Hub, GitMCP, llms.txt): Content flows from source to agent context without any filtering. Security depends entirely on trusting the source and human review of contributions.

2. **Post-hoc sanitization** (Context7 post-patch): Content is filtered after the ContextCrush disclosure, but the filtering implementation is not public and the core architecture still involves injecting external free-form content into agent context.

3. **Structural constraint** (LAP): The compilation step restricts output to a typed grammar, which reduces the attack surface for natural-language injection by design. However, this approach is limited to API specifications and does not cover prose documentation.

The Context Hub vulnerabilities documented in this audit are not unique to Context Hub. They are inherent to any system that takes free-form content from external or community sources and injects it into an AI agent's context window without sanitization. The ContextCrush disclosure in Context7 confirms this is a category-wide problem, not a single-tool failure.

### Sources

- [ContextCrush: The Context7 MCP Server Vulnerability (Noma Security)](https://noma.security/blog/contextcrush-context7-the-mcp-server-vulnerability/)
- [Context7 GitHub Repository (Upstash)](https://github.com/upstash/context7)
- [LAP GitHub Repository](https://github.com/Lap-Platform/LAP)
- [LAP Registry](http://registry.lap.sh/)
- [GitMCP GitHub Repository](https://github.com/idosal/git-mcp)
- [Docfork MCP Server](https://github.com/docfork/docfork)
- [llms.txt Specification](https://llmstxt.org/)
- [Context Hub GitHub Repository](https://github.com/andrewyng/context-hub)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [OWASP LLM Top 10: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
