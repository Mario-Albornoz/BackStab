export type ContactItem = {
  username: string
  link_to_account?: string
}

export type ApiResult =
  | { kind: 'lost'; items: ContactItem[]; note?: string }
  | { kind: 'nonFollowers'; items: ContactItem[]; note?: string }
  | { kind: 'override'; count: number; note: string }
  | { kind: 'none'; note: string }
