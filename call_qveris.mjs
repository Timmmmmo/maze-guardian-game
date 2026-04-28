#!/usr/bin/env node
import { readQverisApiKey } from "./qveris_env.mjs";
import { callTool } from "./qveris_client.mjs";

const apiKey = readQverisApiKey();
const toolId = process.argv[2] || "mcp_gildata.asharelivequote.v1";
const discoveryId = process.argv[3] || "f152cde6-a377-4394-b97f-828ad986bf15";
const query = process.argv[4] || "比亚迪 002594";

const result = await callTool({
  apiKey,
  toolId,
  discoveryId,
  params: { query },
  maxSize: 20480,
  timeoutMs: 60000
});

console.log(JSON.stringify(result, null, 2));