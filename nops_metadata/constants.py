from collections import OrderedDict

from pyrsistent import freeze

SINLE_REGION_SERVICES = freeze(["iam", "s3", "cloudfront"])

# fmt: off
METAMAP = freeze(
    OrderedDict({
        "autoscaling_auto_scaling_groups": {"fetch_method": "describe_auto_scaling_groups", "response_key": "AutoScalingGroups"},
        "cloudformation_stacks": {"fetch_method": "describe_stacks", "response_key": "Stacks"},
        "cloudfront_distributions": {"fetch_method": "list_distributions", "response_key": "Items", "page_key": "DistributionList"},
        "cloudtrail_trails": {"fetch_method": "describe_trails", "response_key": "trailList"},
        "config_configuration_recorder_status": {"fetch_method": "describe_configuration_recorder_status", "response_key": "ConfigurationRecordersStatus"},
        "config_configuration_recorders": {"fetch_method": "describe_configuration_recorders", "response_key": "ConfigurationRecorders"},
        "config_delivery_channel_status": {"fetch_method": "describe_delivery_channel_status", "response_key": "DeliveryChannelsStatus"},
        "config_delivery_channels": {"fetch_method": "describe_delivery_channels", "response_key": "DeliveryChannels"},
        "dynamodb_tables": {"fetch_method": "list_tables", "response_key": "TableNames"},
        "ec2_addresses": {"fetch_method": "describe_addresses", "response_key": "Addresses"},
        "ec2_flow_logs": {"fetch_method": "describe_flow_logs", "response_key": "FlowLogs"},
        "ec2_images": {"fetch_method": "describe_images", "response_key": "Images", "kwargs": {"Owners": ["self"]}},
        "ec2_instances": {"fetch_method": "describe_instances", "page_key": "Reservations", "response_key": "Instances"},
        "ec2_nat_gateways": {"fetch_method": "describe_nat_gateways", "response_key": "NatGateways"},
        "ec2_network_interfaces": {"fetch_method": "describe_network_interfaces", "response_key": "NetworkInterfaces"},
        "ec2_reserved_instances": {"fetch_method": "describe_reserved_instances", "response_key": "ReservedInstances"},
        "ec2_route_tables": {"fetch_method": "describe_route_tables", "response_key": "RouteTables"},
        "ec2_security_groups": {"fetch_method": "describe_security_groups", "response_key": "SecurityGroups"},
        "ec2_snapshots": {"fetch_method": "describe_snapshots", "response_key": "Snapshots", "kwargs": {"OwnerIds": ["self"]}},
        "ec2_subnets": {"fetch_method": "describe_subnets", "response_key": "Subnets"},
        "ec2_volumes": {"fetch_method": "describe_volumes", "response_key": "Volumes"},
        "ec2_vpcs": {"fetch_method": "describe_vpcs", "response_key": "Vpcs"},
        "ecs_clusters": {"fetch_method": "list_clusters", "response_key": "clusterArns"},
        "efs_file_systems": {"fetch_method": "describe_file_systems", "response_key": "FileSystems"},
        "eks_clusters": {"fetch_method": "list_clusters", "response_key": "clusters"},
        "elasticache_cache_clusters": {"fetch_method": "describe_cache_clusters", "response_key": "CacheClusters"},
        "elasticache_replication_groups": {"fetch_method": "describe_replication_groups", "response_key": "ReplicationGroups"},
        "elasticache_cache_subnet_groups": {"fetch_method": "describe_cache_subnet_groups", "response_key": "CacheSubnetGroups"},
        "elbv2_load_balancers": {"fetch_method": "describe_load_balancers", "response_key": "LoadBalancers"},
        "iam_account_aliases": {"fetch_method": "list_account_aliases", "response_key": "AccountAliases"},
        "iam_account_summary": {"fetch_method": "get_account_summary", "response_key": "SummaryMap"},
        "iam_account_password_policy": {"fetch_method": "get_account_password_policy", "response_key": "PasswordPolicy"},
        "iam_roles": {"fetch_method": "list_roles", "response_key": "Roles"},
        "iam_users": {"fetch_method": "list_users", "response_key": "Users"},
        "inspector_assessment_runs": {"fetch_method": "list_assessment_runs", "response_key": "assessmentRunArns"},
        "kms_keys": {"fetch_method": "list_keys", "response_key": "Keys"},
        "lambda_functions": {"fetch_method": "list_functions", "response_key": "Functions"},
        "neptune_db_instances": {"fetch_method": "describe_db_instances", "response_key": "DBInstances"},
        "rds_db_instances": {"fetch_method": "describe_db_instances", "response_key": "DBInstances"},
        "rds_db_snapshots": {"fetch_method": "describe_db_snapshots", "response_key": "DBSnapshots"},
        "rds_pending_maintenance_actions": {"fetch_method": "describe_pending_maintenance_actions", "response_key": "PendingMaintenanceActions"},
        "redshift_clusters": {"fetch_method": "describe_clusters", "response_key": "Clusters"},
        "resourcegroupstaggingapi_tag_keys": {"fetch_method": "get_tag_keys", "response_key": "TagKeys"},
        "resourcegroupstaggingapi_resources": {"fetch_method": "get_resources", "response_key": "ResourceTagMappingList"},
        "s3_buckets": {"fetch_method": "list_buckets", "response_key": "Buckets"},
        "ssm_compliance_summaries": {"fetch_method": "list_compliance_summaries", "response_key": "ComplianceSummaryItems"},
        "workspaces_workspace_directories": {"fetch_method": "describe_workspace_directories", "response_key": "Directories"},
        "workspaces_workspaces": {"fetch_method": "describe_workspaces", "response_key": "Workspaces"},
    })
)

RELATIONSHIPS_MAPPING = freeze(
    {
        "ec2_instances": {
            "volume_fk": {
                "related_table": "ec2_volumes",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.block_device_mappings::jsonb) AS e  INNER JOIN ec2_volumes ec2_volumes_tmp ON (e -> 'Ebs' ->> 'VolumeId') = ec2_volumes_tmp.volume_id""",
                "related_column": "volume_id",
            },
            "image_fk": {
                "related_table": "ec2_images",
                "related_column": "image_id",
            },
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            },
            "subnet_fk": {
                "related_table": "ec2_subnets",
                "related_column": "subnet_id",
            },
        },
        "ec2_security_groups": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            },
        },
        "elbv2_load_balancers": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            },
            "security_groups": {
                "many_to_many": True,
                "m2m_table_name": "elb_security_groups_m2m",
                "related_table": "ec2_security_groups",
                "related_column": "group_id",
            }
        },
        "ec2_snapshots": {
            "volume_fk": {
                "related_table": "ec2_volumes",
                "related_column": "volume_id",
            }
        },
        "ec2_addresses": {
            "instance_fk": {
                "related_table": "ec2_instances",
                "related_column": "instance_id",
            },
            "network_interface_fk": {
                "related_table": "ec2_network_interfaces",
                "related_column": "network_interface_id",
            }
        },
        "ec2_route_tables": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            }
        },
        "ec2_subnets": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            }
        },
        "rds_db_snapshots": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            }
        },
        "ec2_flow_logs": {
            "resource_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
                "this_table_column": "resource_id"
            }
        },
        "ec2_nat_gateways": {
            "subnet_fk": {
                "related_table": "ec2_subnets",
                "related_column": "subnet_id",
            },
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            }
        },
        "autoscaling_auto_scaling_groups": {
            "instances": {
                "many_to_many": True,
                "m2m_table_name": "autoscaling_enabled_ec2_instances",
                "related_table": "ec2_instances",
                "related_column": "instance_id",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.instances::jsonb) AS e INNER JOIN ec2_instances ec2_instances_tmp ON (e ->> 'InstanceId') = ec2_instances_tmp.instance_id """,
            }
        },
        "rds_db_instances": {
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
            "vpc_security_groups": {
                "many_to_many": True,
                "m2m_table_name": "rds_security_groups",
                "related_table": "ec2_security_groups",
                "related_column": "group_id",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.vpc_security_groups::jsonb) AS e INNER JOIN ec2_security_groups ec2_security_groups_tmp ON (e ->> 'VpcSecurityGroupId') = ec2_security_groups_tmp.group_id """,
            }
        },
        "efs_file_systems": {
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
        },
        "elasticache_cache_clusters": {
            "security_groups": {
                "many_to_many": True,
                "m2m_table_name": "elasticache_security_groups",
                "related_table": "ec2_security_groups",
                "related_column": "group_id",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.security_groups::jsonb) AS e INNER JOIN ec2_security_groups ec2_security_groups_tmp ON (e ->> 'SecurityGroupId') = ec2_security_groups_tmp.group_id """,
            },
            "replication_group_pk": {
                "related_table": "elasticache_replication_groups",
                "related_column": "replication_group_id",
            },
            "cache_subnet_group_name_fk": {
                "related_table": "elasticache_cache_subnet_groups",
                "related_column": "cache_subnet_group_name",
            }
        },
        "elasticache_replication_groups": {
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
        },
        "elasticache_cache_subnet_groups": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            },
            "subnets": {
                "many_to_many": True,
                "m2m_table_name": "elasticache_cache_subnet_groups_m2m",
                "related_table": "ec2_subnets",
                "related_column": "subnet_id",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.subnets::jsonb) AS e INNER JOIN ec2_subnets ec2_subnets_tmp ON (e ->> 'SubnetIdentifier') = ec2_subnets_tmp.subnet_id """,
            },
        },
        "redshift_clusters": {
            "vpc_fk": {
                "related_table": "ec2_vpcs",
                "related_column": "vpc_id",
            },
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
        },
        "cloudtrail_trails": {
            "s3_bucket_fk": {
                "related_table": "s3_buckets",
                "related_column": "name",
                "this_table_column": "s3_bucket_name",
            },
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
        },
        "config_delivery_channels": {
            "s3_bucket_fk": {
                "related_table": "s3_buckets",
                "related_column": "name",
                "this_table_column": "s3_bucket_name",
            },
        },
        "cloudformation_stacks": {
            "parent_stack_fk": {
                "related_table": "cloudformation_stacks",
                "related_column": "stack_id",
                "this_table_column": "parent_id",
            },
            "iam_role_fk": {
                "related_table": "iam_roles",
                "related_column": "arn",
                "this_table_column": "role_arn",
            },
        },
        "neptune_db_instances": {
            "vpc_security_groups": {
                "many_to_many": True,
                "m2m_table_name": "neptune_security_groups",
                "related_table": "ec2_security_groups",
                "related_column": "group_id",
                "custom_join_query": """CROSS JOIN LATERAL JSONB_ARRAY_ELEMENTS(vals.vpc_security_groups::jsonb) AS e INNER JOIN ec2_security_groups ec2_security_groups_tmp ON (e ->> 'VpcSecurityGroupId') = ec2_security_groups_tmp.group_id """,
            },
            "kms_key_pk": {
                "related_table": "kms_keys",
                "related_column": "key_arn",
                "this_table_column": "kms_key_id",
            },
        }
    },
)
# fmt: on
