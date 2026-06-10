import { Card, CardContent } from "@/components/ui/card";
import { SidebarContent, SidebarFooter, SidebarProvider, SidebarTrigger, Sidebar, SidebarGroup, SidebarGroupLabel, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";
import { Album, Contact, Info } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

const listItems = [
    {
        name: 'About',
        href: '/dashboard/about',
        icon: <Info/>
    },
    {
        name: 'Records',
        href: '/dashboard/records',
        icon: <Album/>
    },
    {
        name: 'Users',
        href: '/dashboard/users',
        icon: <Contact/>
    }
]

export default function DashboardLayout({ children }) {
    return (
        <>
        <SidebarProvider className={'flex flex-row'}>
            <Sidebar>
                <SidebarContent>
                    <SidebarGroup>
                        <SidebarGroupLabel>Navigation</SidebarGroupLabel>
                        <SidebarGroupContent>
                            <SidebarMenu>
                            {listItems.map((item) => {
                                return <SidebarMenuItem key={item.name}>
                                    <SidebarMenuButton asChild>
                                        <div>
                                            {item.icon}
                                            <Link href={item.href}>{item.name}</Link>
                                        </div>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            })}
                            </SidebarMenu>
                        </SidebarGroupContent>
                    </SidebarGroup>
                </SidebarContent>
                <SidebarFooter>
                    <Card className={'py-2.5 px-0'}>
                        <CardContent className={'flex flex-row justify-between px-2.5'}>
                            <Image src='/user.jpg' className="rounded-xl" width={40} height={40} alt="pfp"></Image>
                            <p>Admin</p>
                        </CardContent>
                    </Card>
                </SidebarFooter>
            </Sidebar>
            <SidebarTrigger/>
            {children}
        </SidebarProvider>
        </>
    )
}