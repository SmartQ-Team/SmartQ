import { createContext, useContext, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Api } from './api';
import type { Me } from './api';

type AuthCtx = {
  me: Me | undefined;
  isLoading: boolean;
  setMe: (user: Me | undefined) => void;
  refresh: () => void;
};

const Ctx = createContext<AuthCtx>({
  me: undefined,
  isLoading: true,
  setMe: () => {},
  refresh: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: Api.me,
    retry: false,
    staleTime: 30_000,
    refetchInterval: (query) => {
      // Stop polling once we know there's no user
      return query.state.data ? 15_000 : false;
    },
  });

  const setMe = useCallback(
    (user: Me | undefined) => {
      qc.setQueryData(['me'], user);
    },
    [qc]
  );

  const refresh = useCallback(() => {
    qc.invalidateQueries({ queryKey: ['me'] });
  }, [qc]);

  return (
    <Ctx.Provider value={{ me: data, isLoading, setMe, refresh }}>
      {children}
    </Ctx.Provider>
  );
}

export const useAuth = () => useContext(Ctx);