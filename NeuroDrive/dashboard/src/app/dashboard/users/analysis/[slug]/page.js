'use client'
import { formatTimeWithMs } from '@/lib/formatting';
import axios from 'axios';
import { use, useEffect, useState } from 'react';
import { Table, TableHeader, TableHead, TableBody, TableCell, TableRow } from '@/components/ui/table';
import { Popover } from '@/components/ui/popover';
import { PopoverContent, PopoverTrigger } from '@radix-ui/react-popover';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DropdownMenu, DropdownMenuContent, DropdownMenuRadioGroup, DropdownMenuTrigger, DropdownMenuRadioItem } from '@/components/ui/dropdown-menu';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Line, LineChart, CartesianGrid, XAxis } from 'recharts';

export default function UserAnalysisPage({ params }) {
    const slug = use(params).slug;
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get(`http://localhost:8080/users/analysis/${slug}`)
            .then(res => {
                setData(res.data);
            })
            .catch(err => {
                console.error("Error fetching user analysis data:", err);
            })
    }, [slug])

    return (
        <div className='flex gap-2 w-dvw mx-6 my-12'>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Serial No.</TableHead>
                        <TableHead>Start Time</TableHead>
                        <TableHead>End Time</TableHead>
                        <TableHead>Samples</TableHead>
                        <TableHead>Prediction</TableHead>
                        <TableHead>View</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data && data.map((r, ind) => (
                        <TableRow key={ind}>
                            <TableCell className="font-medium">{ind + 1}</TableCell>
                            <TableCell>{formatTimeWithMs(r.epoch[0].time)}</TableCell>
                            <TableCell>{formatTimeWithMs(r.epoch[r.epoch.length - 1].time)}</TableCell>
                            <TableCell>{r.epoch.length}</TableCell>
                            <TableCell>{r.prediction}</TableCell>
                            <TableCell>
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <Button>View</Button>
                                    </PopoverTrigger>
                                    <PopoverCard data={r.epoch} />
                                </Popover>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}

function PopoverCard({ data }) {
    const [value, setValue] = useState('eeg1');
    
    return <PopoverContent className='w-120'>
        <Card>
            <CardHeader>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline">{value.toUpperCase()}</Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                        <DropdownMenuRadioGroup value={value} onValueChange={setValue}>
                            <DropdownMenuRadioItem value="eeg1">EEG1</DropdownMenuRadioItem>
                            <DropdownMenuRadioItem value="eeg2">EEG2</DropdownMenuRadioItem>
                            <DropdownMenuRadioItem value="ecg">ECG</DropdownMenuRadioItem>
                        </DropdownMenuRadioGroup>
                    </DropdownMenuContent>
                </DropdownMenu>
            </CardHeader>
            <CardContent>
                <ChartContainer config={{}} className="min-h-[200px] max-w-[400px]">
                    <LineChart width={600} height={600} data={data}>
                        <CartesianGrid vertical={false} />
                        <XAxis
                            dataKey="Id"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                        />
                        <Line dataKey={value} stroke="#f12d2dff" type={'step'} dot={false} strokeWidth={2} />
                        <ChartTooltip
                            cursor={false}
                            content={<ChartTooltipContent hideLabel />}
                        />
                    </LineChart>
                </ChartContainer>
            </CardContent>
        </Card>
    </PopoverContent>;
}

