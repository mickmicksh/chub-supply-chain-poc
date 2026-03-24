FROM node:22-slim

RUN apt-get update && apt-get install -y python3 python3-pip curl && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean

RUN npm install -g @aisuite/chub @anthropic-ai/claude-code

# Create non-root user (Claude Code refuses bypassPermissions as root)
RUN useradd -m -s /bin/bash benchuser
RUN mkdir -p /app/results && chown -R benchuser:benchuser /app

WORKDIR /app

# Which doc to inject. Override with: --build-arg DOC_DIR=stripe-doc
ARG DOC_DIR=plaid-doc
COPY --chown=benchuser:benchuser ${DOC_DIR}/ /app/docs/

# Build chub docs and configure as benchuser
USER benchuser

RUN npx @aisuite/chub build /app/docs

RUN mkdir -p /home/benchuser/.chub && \
    printf 'sources:\n  - name: default\n    url: https://cdn.aichub.org/v1\n  - name: local\n    path: /app/docs/dist\n' > /home/benchuser/.chub/config.yaml

RUN MCP_PATH=$(find / -name "server.js" -path "*chub*mcp*" 2>/dev/null | head -1) && \
    printf '{"mcpServers":{"chub":{"command":"node","args":["%s"]}}}' "$MCP_PATH" > /app/mcp.json

CMD ["bash"]
