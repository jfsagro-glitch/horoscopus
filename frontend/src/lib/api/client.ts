import axios from "axios";
import { appConfig } from "@/lib/config";

export const apiClient = axios.create({
  baseURL: appConfig.apiUrl,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

