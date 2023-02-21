import React, { HTMLAttributes, PropsWithChildren } from 'react'

import NextLink, { LinkProps as NextLinkProps } from 'next/link'

export interface LinkProps extends PropsWithChildren<NextLinkProps & HTMLAttributes<HTMLAnchorElement>> {
  className?: string
}

export function Link({ className, children, href, onClick, ...restProps }: LinkProps) {
  return (
    <NextLink {...restProps} href={href} passHref={false} className={className} onClick={onClick}>
      {children}
    </NextLink>
  )
}