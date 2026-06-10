'use client';
import { Button } from "@/components/ui/button";
import { Table, TableHead, TableHeader, TableRow, TableBody, TableCell } from "@/components/ui/table";
import axios from "axios";
import { useState, useEffect } from "react"

export default function UsersPage() {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        axios.get("http://localhost:8080/users")
            .then(response => {
                setUsers(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the users!", error);
            });
    }, []);

    return <>
    <div className="flex gap-2 w-dvw mx-6 my-12">
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead></TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {users.map(user => (
                    <TableRow key={user.id}>
                        <TableCell className="font-medium">{user.id}</TableCell>
                        <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                        <TableCell>
                            <Button onClick={() => window.location.href = `http://localhost:3000/dashboard/users/analysis/${user.id}`}>Open</Button>
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    </div>
    </>
}