from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as actions,
    aws_logs as logs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class MonitoringStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SNS topic for alarms
        self.alarm_topic = sns.Topic(
            self, "AlarmTopic",
            topic_name=f"{construct_id}-alarms"
        )

        # Create log groups
        # React Apps
        self.lang_portal_cf_logs = logs.LogGroup(
            self, "LangPortalCFLogs",
            log_group_name="/aws/cloudfront/lang-portal",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.haiku_cf_logs = logs.LogGroup(
            self, "HaikuCFLogs",
            log_group_name="/aws/cloudfront/haiku",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Streamlit/Gradio Apps
        self.vocab_frontend_logs = logs.LogGroup(
            self, "VocabFrontendLogs",
            log_group_name="/aws/ecs/vocab-frontend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.writing_practice_logs = logs.LogGroup(
            self, "WritingPracticeLogs",
            log_group_name="/aws/ecs/writing-practice",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Backend Services
        self.lang_portal_backend_logs = logs.LogGroup(
            self, "LangPortalBackendLogs",
            log_group_name="/aws/ecs/lang-portal-backend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.haiku_backend_logs = logs.LogGroup(
            self, "HaikuBackendLogs",
            log_group_name="/aws/ecs/haiku-backend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.vocab_backend_logs = logs.LogGroup(
            self, "VocabBackendLogs",
            log_group_name="/aws/ecs/vocab-backend",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Infrastructure Logs
        self.aurora_logs = logs.LogGroup(
            self, "AuroraLogs",
            log_group_name="/aws/rds/aurora",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create CloudWatch Dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "MainDashboard",
            dashboard_name=f"{construct_id}-main"
        )

        # Add widgets to dashboard
        self.dashboard.add_widgets(
            # Application Health
            cloudwatch.Row(
                cloudwatch.GraphWidget(
                    title="5XX Errors",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/ApplicationELB",
                            metric_name="HTTPCode_Target_5XX_Count",
                            statistic="sum",
                            period=Duration.minutes(1)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="4XX Errors",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/ApplicationELB",
                            metric_name="HTTPCode_Target_4XX_Count",
                            statistic="sum",
                            period=Duration.minutes(1)
                        )
                    ]
                )
            ),
            # Service Health
            cloudwatch.Row(
                cloudwatch.GraphWidget(
                    title="CPU Utilization",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/ECS",
                            metric_name="CPUUtilization",
                            statistic="average",
                            period=Duration.minutes(1)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="Memory Utilization",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/ECS",
                            metric_name="MemoryUtilization",
                            statistic="average",
                            period=Duration.minutes(1)
                        )
                    ]
                )
            ),
            # Database Health
            cloudwatch.Row(
                cloudwatch.GraphWidget(
                    title="Database Connections",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/RDS",
                            metric_name="DatabaseConnections",
                            statistic="average",
                            period=Duration.minutes(1)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="DB CPU Utilization",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/RDS",
                            metric_name="CPUUtilization",
                            statistic="average",
                            period=Duration.minutes(1)
                        )
                    ]
                )
            )
        )

        # Create Alarms
        # High Priority Alarms
        self.error_rate_alarm = cloudwatch.Alarm(
            self, "ErrorRateAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ApplicationELB",
                metric_name="HTTPCode_Target_5XX_Count",
                statistic="sum",
                period=Duration.minutes(1)
            ),
            threshold=5,
            evaluation_periods=5,
            alarm_description="5XX error rate exceeded threshold",
            alarm_name=f"{construct_id}-5xx-errors",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        self.error_rate_alarm.add_alarm_action(actions.SnsAction(self.alarm_topic))

        self.cpu_alarm = cloudwatch.Alarm(
            self, "CPUAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ECS",
                metric_name="CPUUtilization",
                statistic="average",
                period=Duration.minutes(5)
            ),
            threshold=85,
            evaluation_periods=3,
            alarm_description="CPU utilization exceeded threshold",
            alarm_name=f"{construct_id}-cpu-high",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        self.cpu_alarm.add_alarm_action(actions.SnsAction(self.alarm_topic))

        # Database Alarms
        self.db_connections_alarm = cloudwatch.Alarm(
            self, "DBConnectionsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/RDS",
                metric_name="DatabaseConnections",
                statistic="average",
                period=Duration.minutes(5)
            ),
            threshold=100,
            evaluation_periods=3,
            alarm_description="Database connections exceeded threshold",
            alarm_name=f"{construct_id}-db-connections",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        self.db_connections_alarm.add_alarm_action(actions.SnsAction(self.alarm_topic))

        # Outputs
        CfnOutput(self, "DashboardName",
            value=self.dashboard.dashboard_name,
            description="Main CloudWatch Dashboard name",
            export_name=f"{construct_id}-dashboard-name"
        )

        CfnOutput(self, "AlarmTopicArn",
            value=self.alarm_topic.topic_arn,
            description="SNS topic ARN for alarms",
            export_name=f"{construct_id}-alarm-topic-arn"
        )