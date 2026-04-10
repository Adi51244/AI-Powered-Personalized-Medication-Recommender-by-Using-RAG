'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import Link from 'next/link'

interface PatientStats {
  totalDiagnoses: number
  totalMedications: number
  recentDiagnosis: any
  analytics: {
    conditionsAnalyzed: number
    medicinesPrescribed: number
    safetyChecks: number
  }
}

export function PatientDashboard({ userId }: { userId: string }) {
  const [stats, setStats] = useState<PatientStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [diagnoses, setDiagnoses] = useState<any[]>([])

  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/patients/${userId}/diagnoses`
        )
        if (response.ok) {
          const data = await response.json()
          setDiagnoses(data.diagnoses || [])

          setStats({
            totalDiagnoses: data.diagnoses?.length || 0,
            totalMedications: data.diagnoses?.reduce(
              (sum: number, d: any) => sum + (d.medications?.length || 0),
              0
            ) || 0,
            recentDiagnosis: data.diagnoses?.[0] || null,
            analytics: {
              conditionsAnalyzed: data.diagnoses?.length || 0,
              medicinesPrescribed:
                data.diagnoses?.reduce(
                  (sum: number, d: any) => sum + (d.medications?.length || 0),
                  0
                ) || 0,
              safetyChecks: data.diagnoses?.length || 0,
            },
          })
        }
      } catch (error) {
        console.error('Failed to fetch patient data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPatientData()
  }, [userId])

  if (loading) {
    return <div className="text-center">Loading your dashboard...</div>
  }

  return (
    <Tabs defaultValue="overview" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="diagnoses">Diagnoses</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>

      {/* Overview Tab */}
      <TabsContent value="overview" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Diagnoses
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalDiagnoses || 0}</div>
              <p className="text-xs text-gray-500">diagnoses analyzed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Medications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalMedications || 0}</div>
              <p className="text-xs text-gray-500">medications recommended</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Safety Checks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.analytics.safetyChecks || 0}</div>
              <p className="text-xs text-gray-500">safety validations</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Get a New Diagnosis</CardTitle>
            <CardDescription>
              Start a new diagnosis session
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/diagnose">
              <Button>Start Diagnosis</Button>
            </Link>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Diagnoses Tab */}
      <TabsContent value="diagnoses" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Your Diagnoses</CardTitle>
          </CardHeader>
          <CardContent>
            {diagnoses.length === 0 ? (
              <p className="text-gray-500">No diagnoses yet</p>
            ) : (
              <div className="space-y-4">
                {diagnoses.map((diagnosis, index) => (
                  <div key={index} className="border rounded p-4">
                    <h3 className="font-semibold">{diagnosis.primary_diagnosis}</h3>
                    <p className="text-sm text-gray-600">
                      Confidence: {(diagnosis.confidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(diagnosis.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* Analytics Tab */}
      <TabsContent value="analytics" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Conditions Analyzed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats?.analytics.conditionsAnalyzed || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Medicines Prescribed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats?.analytics.medicinesPrescribed || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      </TabsContent>
    </Tabs>
  )
}
