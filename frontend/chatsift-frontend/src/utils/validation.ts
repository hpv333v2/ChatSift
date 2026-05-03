import { z } from 'zod';

export const emailSchema = z.string().email('Invalid email address');

// Backend uses Django's default validators: MinimumLength=8, no other requirements
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters');

export const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters')
  .max(30, 'Username must be at most 30 characters')
  .regex(
    /^[a-zA-Z0-9_-]+$/,
    'Username can only contain letters, numbers, underscores, and hyphens'
  );

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z
  .object({
    email: emailSchema,
    username: usernameSchema,
    password: passwordSchema,
    password_confirm: z.string().min(1, 'Please confirm your password'),
    first_name: z.string().optional(),
    last_name: z.string().optional(),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  });

export const emailVerifySchema = z.object({
  token: z.string().min(1, 'Token is required'),
  uid: z.string().min(1, 'UID is required'),
});

// Made with Bob
