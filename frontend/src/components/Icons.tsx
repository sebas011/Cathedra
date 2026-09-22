import type { SVGProps } from "react";

type Props = SVGProps<SVGSVGElement>;
const Icon = ({ children, ...props }: Props) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{children}</svg>;

export const DashboardIcon = (p: Props) => <Icon {...p}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></Icon>;
export const FsdpIcon = (p: Props) => <Icon {...p}><path d="M4 6h16v14H4z"/><path d="M8 6V4h8v2"/><path d="M8 11h8M8 15h5"/></Icon>;
export const ReviewIcon = (p: Props) => <Icon {...p}><path d="M5 4h11l3 3v13H5z"/><path d="M8 11h7M8 15h4"/><path d="m14 4 3 3"/></Icon>;
export const WorkloadIcon = (p: Props) => <Icon {...p}><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></Icon>;
export const ExpenseIcon = (p: Props) => <Icon {...p}><circle cx="12" cy="12" r="9"/><path d="M15 8.5c-.7-.7-1.7-1-3-1-1.7 0-3 .8-3 2s1 1.8 3 2.2 3 1 3 2.3-1.3 2.2-3 2.2c-1.4 0-2.5-.4-3.2-1.2M12 5.5v13"/></Icon>;
export const BackupIcon = (p: Props) => <Icon {...p}><path d="M4 4h12l4 4v12H4z"/><path d="M8 4v6h8V4M8 20v-6h8v6"/></Icon>;
export const SearchIcon = (p: Props) => <Icon {...p}><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></Icon>;
export const PlusIcon = (p: Props) => <Icon {...p}><path d="M12 5v14M5 12h14"/></Icon>;
export const MenuIcon = (p: Props) => <Icon {...p}><path d="M4 7h16M4 12h16M4 17h16"/></Icon>;
export const UserIcon = (p: Props) => <Icon {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></Icon>;
export const LogoutIcon = (p: Props) => <Icon {...p}><path d="M9 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4M16 17l5-5-5-5M21 12H9"/></Icon>;
export const EditIcon = (p: Props) => <Icon {...p}><path d="m4 20 4.5-1 10-10a2.1 2.1 0 0 0-3-3l-10 10L4 20Z"/><path d="m14 7 3 3"/></Icon>;
export const TrashIcon = (p: Props) => <Icon {...p}><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5"/></Icon>;
export const ArrowIcon = (p: Props) => <Icon {...p}><path d="M5 12h14M13 6l6 6-6 6"/></Icon>;
