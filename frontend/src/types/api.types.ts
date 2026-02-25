export type ApiOk<T> = {
  success: true;
  data: T;
};

export type ApiErr = {
  success: false;
  error: { code: string; message: string; details?: unknown };
};