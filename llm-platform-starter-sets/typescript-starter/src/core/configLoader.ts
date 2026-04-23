/**
 * configLoader.ts — Reads client and module JSON config files.
 */

import * as fs from "fs";
import * as path from "path";
import { ClientConfig, ModuleConfig } from "./types";

const CONFIG_DIR = path.resolve(__dirname, "../../config");

export function loadClient(clientId: string): ClientConfig {
  const filePath = path.join(CONFIG_DIR, "clients", `${clientId}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Client config not found: ${filePath}`);
  }
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as ClientConfig;
}

export function loadModuleConfig(moduleName: string): ModuleConfig {
  const filePath = path.join(CONFIG_DIR, "modules", `${moduleName}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Module config not found: ${filePath}`);
  }
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as ModuleConfig;
}

export function getClientTone(client: ClientConfig): string {
  return client.branding?.tone ?? "clear and professional";
}

export function getClientPermissions(client: ClientConfig, moduleName: string): string[] {
  return client.permissions?.[moduleName] ?? [];
}
