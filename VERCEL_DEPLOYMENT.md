# Vercel deployment (experimental)

This branch adds a Vercel Python ASGI entrypoint for the existing FastMCP server.
The existing server implementation and tool registrations are not changed.

## Vercel project settings

- Framework preset: Other (or let Vercel detect the Python Function)
- Root directory: repository root
- Production branch: `vercel-deployment`
- Python runtime: use the version selected by Vercel from the project metadata.

## Environment variables

Configure these in Vercel Project Settings → Environment Variables:

- `INTERVALS_ICU_API_KEY`: your Intervals.icu API key
- `INTERVALS_ICU_ATHLETE_ID`: your athlete ID
- `INTERVALS_ICU_DELETE_MODE`: `safe` (recommended), `full`, or `none`
- `MCP_AUTH_TOKEN`: a long, random secret used as HTTP Bearer authentication

Do not commit these values to Git. Do not share the token in screenshots or chat.

## Endpoint and authentication

The function is exposed at:

`https://YOUR-PROJECT.vercel.app/api`

Requests must include:

`Authorization: Bearer YOUR_MCP_AUTH_TOKEN`

The endpoint is stateless Streamable HTTP. The bearer-token middleware is placed in front of the MCP app because the upstream project documents that its HTTP transport has no built-in authentication.

## Important limits / validation

This is an experimental deployment target. Vercel Python Functions are request-scoped serverless functions, not a permanently running container. The Hobby plan has a maximum function duration of 60 seconds. Long-running tool calls may time out.

Before switching clients from Railway:
1. Deploy this branch as a separate Vercel project.
2. Set all environment variables.
3. Confirm an unauthenticated request returns HTTP 401.
4. Connect with the MCP URL and Bearer token.
5. Test representative read-only tools first, then test write tools only if needed.
6. Keep Railway running until the Vercel deployment has passed real ChatGPT tests.

If FastMCP's ASGI lifespan is not invoked correctly by the Python runtime, the endpoint may fail during MCP initialization. Check Vercel runtime logs before changing the production endpoint.
