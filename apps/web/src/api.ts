import { getHealth, type ServiceStatus } from "@open-hollywood/contracts";
import { client } from "@open-hollywood/contracts/client";

const apiBaseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

client.setConfig({ baseUrl: apiBaseUrl });

export async function fetchServiceStatus(): Promise<ServiceStatus> {
  const result = await getHealth();

  if (result.error) {
    throw new Error("The local Open Hollywood API did not accept the request.");
  }

  if (!result.data) {
    throw new Error("The local Open Hollywood API returned no service status.");
  }

  return result.data;
}
