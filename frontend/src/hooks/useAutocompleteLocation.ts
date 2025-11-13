import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { apiClient } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { LocationSuggestion } from "@/lib/types";

interface UseAutocompleteLocationOptions {
  query: string;
  limit?: number;
  enabled?: boolean;
}

export function useAutocompleteLocation({
  query,
  limit = 6,
  enabled = true,
}: UseAutocompleteLocationOptions) {
  const normalized = query.trim();

  const result = useQuery({
    queryKey: ["locations", "autocomplete", normalized, limit],
    queryFn: async () => {
      const response = await apiClient.get<LocationSuggestion[]>(
        endpoints.locations.autocomplete,
        {
          params: { q: normalized, limit },
        },
      );
      return response.data;
    },
    enabled: enabled && normalized.length >= 3,
  });

  return useMemo(
    () => ({
      suggestions: result.data ?? [],
      isLoading: result.isFetching,
    }),
    [result.data, result.isFetching],
  );
}

