import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const path = request.nextUrl.pathname;

  // List of protected routes as requested
  const protectedRoutes = ['/', '/overview', '/analytics', '/ask', '/documents', '/search'];

  const isProtectedRoute = protectedRoutes.some(route => 
    route === '/' ? path === '/' : path.startsWith(route)
  );

  // If trying to access a protected route without a token, redirect to login
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
