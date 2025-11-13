export interface LocationSuggestion {
  id: number;
  name: string;
  city: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  score: number;
}

export interface BirthDataPayload {
  birthDate: string;
  birthTime: string;
  timezone: string;
  locationId: number;
  currentLocationId?: number;
}

