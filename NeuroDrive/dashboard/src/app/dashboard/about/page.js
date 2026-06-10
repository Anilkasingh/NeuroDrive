import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import Image from "next/image";

export default function About() {
    return (
        <div className="flex flex-col items-center w-full min-h-[80vh] p-6">
            <div className="w-full max-w-3xl">
                <Card>
                    <CardHeader>
                        <h1 className="text-3xl font-bold text-primary mb-2">About Our EEG Dashboard</h1>
                        <Separator className="my-2" />
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col md:flex-row gap-8 items-center mb-8">
                            <div className="flex-1 h-40 bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-lg">
                                {/* Replace with an actual image if available */}
                                <span>Image Placeholder 1</span>
                            </div>
                            <div className="flex-1">
                                <p className="text-base text-muted-foreground leading-relaxed">
                                    This dashboard provides intuitive visualization and analysis tools for EEG data. Designed for researchers and clinicians, it offers real-time insights, customizable reports, and seamless data management.
                                </p>
                            </div>
                        </div>
                        <div className="flex flex-col md:flex-row gap-8 items-center">
                            <div className="flex-1 order-2 md:order-1">
                                <p className="text-base text-muted-foreground leading-relaxed">
                                    Explore interactive charts, monitor trends, and collaborate with your team. Our mission is to make EEG data accessible and actionable for everyone.
                                </p>
                            </div>
                            <div className="flex-1 h-40 rounded-lg flex items-center justify-center text-muted-foreground text-lg order-1 md:order-2">
                                {/* Replace with an actual image if available */}
                                <Image src="/plot.png" alt="EEG Visualization" width="300" height={250} className="rounded-lg" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}