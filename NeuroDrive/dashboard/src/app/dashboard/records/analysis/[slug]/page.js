"use client";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from "recharts";
import { use, useEffect, useState } from "react";
import axios from "axios";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatDate, formatTimeWithMs } from "@/lib/formatting";
import { Input } from "@/components/ui/input";

function Matcher({ prediction }) {
    const [verdict, setVerdict] = useState("");
    const isMatch = verdict.trim().toLowerCase() === String(prediction).trim().toLowerCase();
    const Icon = isMatch ? require("lucide-react").CheckCircle : require("lucide-react").XCircle;

    return (
        <>
            <Input
                type="text"
                className="border p-1"
                placeholder="Enter verdict"
                value={verdict}
                onChange={(e) => setVerdict(e.target.value)}
            />
            {verdict && (
                <div className="mt-2 flex justify-center">
                    <Icon color={isMatch ? "green" : "red"} size={24} />
                </div>
            )}
        </>
    );
}

export default function Page({ params }) {
    const slug = use(params).slug;
    const [data, setData] = useState(null);
    const [plot, setPlot] = useState(null);
    const [processed, setProcessed] = useState([]);
    const [loading, setLoading] = useState(false);

    function processData() {
        setLoading(true);
        axios.get(`http://localhost:8080/recordings/analysis/${slug}`)
            .then(res => {
                setProcessed(res.data);
            })
            .catch(err => {
                console.log(err);
            })
            .finally(() => {
                setLoading(false);
            });
    }

    const channels = ['eeg1', 'eeg2', 'ecg'];

    useEffect(() => {
        axios.get(`http://localhost:8080/recordings/${slug}`)
            .then(res => {
                if (res.data && res.data.samples) {
                    setData(res.data);
                }
            })
            .catch(err => {
                console.log(err);
            });
    }, [slug]);

    return (
        <div className="flex flex-row gap-2 w-full p-3.5">
            {data &&
                <div className="flex-1 flex-column gap-2 mt-2.5 overflow-y-auto" style={{ maxHeight: '95vh' }}>
                    <div className="flex flex-row gap-2">
                        <div className="mb-2.5 flex-3">
                            <p className="text-xl"><b>Name:</b> {`${data.user.first_name} ${data.user.last_name}`}</p>
                            <p className="text-xl"><b>Starting Time:</b> {formatDate(data.timeFrom)}</p>
                            <p className="text-xl"><b>Ending Time:</b> {formatDate(data.timeTo)}</p>
                            <p className="text-xl"><b>Recording ID:</b> {data.id}</p>
                        </div>
                        <div className="flex-1">
                            <Button variant="secondary" onClick={() => setPlot(data.samples)}>Show Overall</Button>
                        </div>
                    </div>

                    {processed && processed.length == 0 &&
                        <Button onClick={processData}>Run data through model</Button>
                    }
                    {loading && <p>Loading!</p>}
                    {processed && processed.length > 0 &&
                        processed.map((item, index) => <Card key={index} className="mb-2">
                            <CardHeader>
                                <h3 className="text-lg font-medium">Prediction: {item.prediction}</h3>
                            </CardHeader>
                            <CardContent className="flex flex-row justify-between">
                                <div className="flex-1">
                                    <p className="text-sm">Time From: {formatTimeWithMs(item.epoch[0].time)}</p>
                                    <p className="text-sm">Time To: {formatTimeWithMs(item.epoch[item.epoch.length - 1].time)}</p>
                                    <Button variant='secondary' className="mt-2.5" onClick={() => setPlot(item.epoch)}>Show Data</Button>
                                </div>
                            </CardContent>
                        </Card>)
                    }

                </div>
            }

            <div className="flex-1 flex-column gap-2 m-2.5 overflow-y-auto" style={{ maxHeight: '95vh' }}>
                {plot && plot.length > 0 &&
                    channels.map(channel =>
                        <Card key={channel} className={"mb-2"}>
                            <CardHeader>
                                <h3 className="text-lg font-medium">{channel.toUpperCase()}</h3>
                            </CardHeader>
                            <CardContent>
                                <ChartContainer config={{}} className="min-h-[200px] max-w-[400px]">
                                    <LineChart width={600} height={600} data={plot}>
                                        <CartesianGrid vertical={false} />
                                        <XAxis
                                            dataKey="Id"
                                            tickLine={false}
                                            axisLine={false}
                                            tickMargin={8}
                                        // tickFormatter={(value) => value.slice(0, 3)}
                                        />
                                        <Line dataKey={channel} stroke="#8884d8" type={'step'} dot={false} strokeWidth={2} />
                                        <ChartTooltip
                                            cursor={false}
                                            content={<ChartTooltipContent hideLabel />}
                                        />
                                    </LineChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                    )}
            </div>
        </div>
    );
}
