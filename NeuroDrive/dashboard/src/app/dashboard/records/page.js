'use client';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableRow, TableBody, TableCell, TableHead } from "@/components/ui/table";
import { formatDate } from "@/lib/formatting";
import { LucideArrowLeft, LucideSearch, LucideArrowRight } from "lucide-react";
import {useState, useEffect } from 'react';
import axios from "axios";

export default function RecordPage() {
    const [ records, setRecords ] = useState([]);
    const [ data, setData ] = useState([]);
    const [ page, setPage ] = useState(1);
    useEffect(() => {
        axios.get('http://localhost:8080/recordings')
            .then(response => {
                setRecords(response.data);
                setData(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the records!", error);
            });
        console.log(records)
    }, [])

    useEffect(() => {
        const searchInput = document.getElementById('table-search');
        const handleSearch = () => {
            if (searchInput.value.trim() === '') {
                setRecords(data);
            } else {
                const searchTerm = searchInput.value.trim().toLowerCase();
                setRecords(data.filter(record => {
                    return (
                        record.user.first_name.toLowerCase().includes(searchTerm) ||
                        record.user.last_name.toLowerCase().includes(searchTerm) ||
                        record.id.toString().includes(searchTerm)
                    );
                }));
            }
        };

        searchInput.addEventListener('input', handleSearch);

        return () => {
            searchInput.removeEventListener('input', handleSearch);
        };
    }, [data]);

    return (
        <div className='flex flex-col gap-2 w-dvw mx-6 my-12'>
            <div className="flex flex-row justify-items-start gap-2">
                <Input id="table-search" placeholder="Search" className='flex-1/3' />
                <Button variant='secondary' size='icon' >
                    <LucideSearch/>
                </Button>
                <div className="flex-1/2"></div>
            </div>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Start Time</TableHead>
                        <TableHead>End Time</TableHead>
                        <TableHead></TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {records && records.map(r => (
                        <TableRow key={r.id}>
                            <TableCell className="font-medium">{r.id}</TableCell>
                            <TableCell>{`${r.user.first_name} ${r.user.last_name}`}</TableCell>
                            <TableCell>{formatDate(r.timeFrom)}</TableCell>
                            <TableCell>{formatDate(r.timeTo)}</TableCell>
                            <TableCell>
                                <Button onClick={() => window.location.href = `/dashboard/records/analysis/${r.id}`}>Open</Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <div className="flex flex-row justify-center gap-2">
                <Button size='icon' variant='secondary' onClick={() => setPage(page => page - 1)}>
                    <LucideArrowLeft/>
                </Button>
                <Button size='icon' variant='secondary' onClick={() => setPage(page => page + 1)}>
                    <LucideArrowRight/>
                </Button>
            </div>
            <span className="text-neutral-400 text-sm text-center">Select a record to get started</span>
        </div>
    )
}